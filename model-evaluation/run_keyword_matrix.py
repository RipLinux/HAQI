import json
import statistics
import time
from pathlib import Path

import psycopg

ROOT = Path(__file__).parents[1]
DATA = ROOT / "data" / "evaluation" / "model_comparison"
RESULTS = Path(__file__).parent / "results"
DATABASE_URL = "host=localhost port=5432 dbname=haqi user=haqi password=haqi_dev_password"
SCHEMA = "retrieval_keyword_matrix"


def dcg(values: list[float]) -> float:
    import math

    return sum((2**value - 1) / math.log2(rank + 2) for rank, value in enumerate(values))


def metrics(ids: list[str], judgment: dict[str, object], k: int) -> dict[str, float]:
    relevant = {str(value) for value in judgment["relevant_chunk_ids"]}
    grades = {str(key): float(value) for key, value in judgment["relevance"].items()}
    top = ids[:k]
    ideal = dcg(sorted(grades.values(), reverse=True)[:k])
    return {
        "recall": len(set(top) & relevant) / len(relevant) if relevant else 0.0,
        "precision": len(set(top) & relevant) / k,
        "mrr": next((1 / rank for rank, value in enumerate(top, 1) if value in relevant), 0.0),
        "ndcg": dcg([grades.get(value, 0.0) for value in top]) / ideal if ideal else 0.0,
    }


def percentile(values: list[float], quantile: float) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    position = (len(values) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def main() -> None:
    chunks = [json.loads(line) for line in (DATA / "synthetic_chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    queries = [json.loads(line) for line in (DATA / "synthetic_queries.jsonl").read_text(encoding="utf-8").splitlines()]
    judgments = {
        row["query_id"]: row
        for row in (
            json.loads(line)
            for line in (DATA / "relevance_judgments.jsonl").read_text(encoding="utf-8").splitlines()
        )
    }
    methods = ["exact", "token_or", "simple", "arabic", "english"]
    result_rows: dict[str, list[dict[str, object]]] = {method: [] for method in methods}
    with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
            cursor.execute(f"CREATE SCHEMA {SCHEMA}")
            cursor.execute(
                f"CREATE TABLE {SCHEMA}.chunks (chunk_id text PRIMARY KEY, text text NOT NULL, language text NOT NULL)"
            )
            for row in chunks:
                cursor.execute(
                    f"INSERT INTO {SCHEMA}.chunks VALUES (%s, %s, %s)",
                    (row["chunk_id"], row["text"], row["language"]),
                )
            cursor.execute("SELECT cfgname FROM pg_ts_config ORDER BY cfgname")
            configurations = [row[0] for row in cursor.fetchall()]
            has_trgm = False
            cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'pg_trgm')")
            has_trgm = bool(cursor.fetchone()[0])
            if has_trgm:
                cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm')")
                has_trgm = bool(cursor.fetchone()[0])
            if has_trgm:
                methods.append("trgm")
            for query in queries:
                judgment = judgments[query["query_id"]]
                text_value = query["query"]
                for method in methods:
                    started = time.perf_counter()
                    if method == "exact":
                        cursor.execute(
                            f"SELECT chunk_id FROM {SCHEMA}.chunks "
                            "WHERE lower(text) LIKE '%%' || lower(%s) || '%%' "
                            "ORDER BY chunk_id LIMIT 10",
                            (text_value,),
                        )
                    elif method == "token_or":
                        cursor.execute(
                            f"SELECT chunk_id FROM {SCHEMA}.chunks "
                            "WHERE EXISTS ("
                            "SELECT 1 FROM regexp_split_to_table(lower(%s), E'[^[:alnum:]\\u0600-\\u06ff]+') AS q(token) "
                            "WHERE length(q.token) > 2 AND lower(text) LIKE '%%' || q.token || '%%') "
                            "ORDER BY chunk_id LIMIT 10",
                            (text_value,),
                        )
                    elif method in {"simple", "arabic", "english"}:
                        cursor.execute(
                            f"SELECT chunk_id FROM {SCHEMA}.chunks "
                            f"WHERE to_tsvector('{method}', text) @@ plainto_tsquery('{method}', %s) "
                            f"ORDER BY ts_rank_cd(to_tsvector('{method}', text), plainto_tsquery('{method}', %s)) DESC, chunk_id LIMIT 10",
                            (text_value, text_value),
                        )
                    else:
                        cursor.execute(
                            f"SELECT chunk_id FROM {SCHEMA}.chunks "
                            "ORDER BY word_similarity(text, %s) DESC, chunk_id LIMIT 10",
                            (text_value,),
                        )
                    ids = [row[0] for row in cursor.fetchall()]
                    latency_ms = (time.perf_counter() - started) * 1000
                    result_rows[method].append(
                        {
                            "query_id": query["query_id"],
                            "language": query["language"],
                            "retrieved": ids,
                            "latency_ms": latency_ms,
                            **metrics(ids, judgment, 5),
                            **{f"{key}10": value for key, value in metrics(ids, judgment, 10).items()},
                        }
                    )
    report: dict[str, object] = {
        "ts_configurations": configurations,
        "pg_trgm_already_enabled": has_trgm,
        "dataset_queries": len(queries),
        "methods": {},
    }
    for method, rows in result_rows.items():
        report["methods"][method] = {}
        for language in ["ar_msa", "ar_egy", "en", "overall"]:
            selected = rows if language == "overall" else [row for row in rows if row["language"] == language]
            latencies = [float(row["latency_ms"]) for row in selected]
            report["methods"][method][language] = {
                metric: statistics.fmean(float(row[metric]) for row in selected) if selected else 0.0
                for metric in (
                    "recall",
                    "precision",
                    "mrr",
                    "ndcg",
                    "recall10",
                    "precision10",
                    "mrr10",
                    "ndcg10",
                )
            }
            report["methods"][method][language].update(
                {
                    "average_latency_ms": statistics.fmean(latencies) if latencies else 0.0,
                    "p50_latency_ms": percentile(latencies, 0.5),
                    "p95_latency_ms": percentile(latencies, 0.95),
                }
            )
        (RESULTS / f"keyword_{method}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    (RESULTS / "keyword_matrix_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
