import csv
import json
import statistics
import sys
import time
from pathlib import Path

import psycopg
from sentence_transformers import CrossEncoder, SentenceTransformer


ROOT = Path(__file__).parents[1]
DATA = ROOT / "data" / "evaluation" / "model_comparison"
RESULTS = Path(__file__).parent / "results"
DATABASE_URL = "host=localhost port=5432 dbname=haqi user=haqi password=haqi_dev_password"


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def dcg(values: list[float]) -> float:
    import math

    return sum((2**value - 1) / math.log2(rank + 2) for rank, value in enumerate(values))


def metric_summary(retrieved: list[str], judgment: dict[str, object], k: int) -> dict[str, float]:
    relevant = {str(value) for value in judgment["relevant_chunk_ids"]}
    grades = {str(key): float(value) for key, value in judgment["relevance"].items()}
    top = retrieved[:k]
    hits = len(set(top) & relevant)
    mrr = next((1 / rank for rank, value in enumerate(top, 1) if value in relevant), 0.0)
    ideal = dcg(sorted(grades.values(), reverse=True)[:k])
    return {
        "recall": hits / len(relevant) if relevant else 0.0,
        "precision": hits / k,
        "mrr": mrr,
        "ndcg": dcg([grades.get(value, 0.0) for value in top]) / ideal if ideal else 0.0,
    }


def percentile(values: list[float], value: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * value
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def main() -> None:
    model_id = sys.argv[1] if len(sys.argv) > 1 else "intfloat/multilingual-e5-small"
    label = "minilm" if "paraphrase-multilingual" in model_id else "e5"
    schema = f"retrieval_model_comparison_{label}"
    prefix_query = "query: " if label == "e5" else ""
    prefix_passage = "passage: " if label == "e5" else ""
    chunks = [json.loads(line) for line in (DATA / "synthetic_chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    queries = [json.loads(line) for line in (DATA / "synthetic_queries.jsonl").read_text(encoding="utf-8").splitlines()]
    judgments = {
        row["query_id"]: row
        for row in (json.loads(line) for line in (DATA / "relevance_judgments.jsonl").read_text(encoding="utf-8").splitlines())
    }
    embedding = SentenceTransformer(model_id, device="cpu")
    reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1", device="cpu")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
            cursor.execute(f"CREATE SCHEMA {schema}")
            cursor.execute(
                f"CREATE TABLE {schema}.chunks ("
                "chunk_id text PRIMARY KEY, document_id text NOT NULL, text text NOT NULL, "
                "language text NOT NULL, source_identifier text NOT NULL, embedding vector(384) NOT NULL)"
            )
            passage_vectors = embedding.encode(
                [prefix_passage + row["text"] for row in chunks],
                normalize_embeddings=True,
                convert_to_numpy=True,
                batch_size=16,
                show_progress_bar=False,
            )
            for row, vector in zip(chunks, passage_vectors):
                cursor.execute(
                    f"INSERT INTO {schema}.chunks VALUES (%s, %s, %s, %s, %s, %s::vector)",
                    (
                        row["chunk_id"],
                        row["document_id"],
                        row["text"],
                        row["language"],
                        row["source_identifier"],
                        vector_literal(vector.tolist()),
                    ),
                )
            cursor.execute(f"CREATE INDEX chunks_embedding_hnsw ON {schema}.chunks USING hnsw (embedding vector_cosine_ops)")
            cursor.execute(f"SELECT count(*) FROM {schema}.chunks")
            indexed_chunks = cursor.fetchone()[0]
            measurements: dict[str, list[dict[str, object]]] = {name: [] for name in ("vector", "keyword", "hybrid", "reranked")}
            for query in queries:
                judgment = judgments[query["query_id"]]
                query_text = query["query"]
                embedding_start = time.perf_counter()
                query_vector = embedding.encode(
                    [prefix_query + query_text],
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )[0]
                embedding_ms = (time.perf_counter() - embedding_start) * 1000
                vector_start = time.perf_counter()
                cursor.execute(
                    f"SELECT chunk_id, document_id, text, source_identifier, 1 - (embedding <=> %s::vector) AS score "
                    f"FROM {schema}.chunks ORDER BY embedding <=> %s::vector LIMIT 10",
                    (vector_literal(query_vector.tolist()), vector_literal(query_vector.tolist())),
                )
                vector_rows = cursor.fetchall()
                vector_ms = (time.perf_counter() - vector_start) * 1000
                keyword_start = time.perf_counter()
                cursor.execute(
                    f"SELECT chunk_id, document_id, text, source_identifier, "
                    f"ts_rank_cd(to_tsvector('simple', text), plainto_tsquery('simple', %s)) AS score "
                    f"FROM {schema}.chunks "
                    "WHERE to_tsvector('simple', text) @@ plainto_tsquery('simple', %s) "
                    "ORDER BY score DESC, chunk_id LIMIT 10",
                    (query_text, query_text),
                )
                keyword_rows = cursor.fetchall()
                keyword_ms = (time.perf_counter() - keyword_start) * 1000
                vector_ids = [row[0] for row in vector_rows]
                keyword_ids = [row[0] for row in keyword_rows]
                fusion_start = time.perf_counter()
                rank_map = {}
                row_map = {row[0]: row for row in vector_rows + keyword_rows}
                for rank, chunk_id in enumerate(vector_ids, 1):
                    rank_map[chunk_id] = rank_map.get(chunk_id, 0.0) + 1 / (60 + rank)
                for rank, chunk_id in enumerate(keyword_ids, 1):
                    rank_map[chunk_id] = rank_map.get(chunk_id, 0.0) + 1 / (60 + rank)
                hybrid_ids = sorted(rank_map, key=lambda value: (-rank_map[value], value))[:10]
                fusion_ms = (time.perf_counter() - fusion_start) * 1000
                rerank_start = time.perf_counter()
                rerank_scores = reranker.predict(
                    [[query_text, row_map[chunk_id][2]] for chunk_id in hybrid_ids],
                    batch_size=8,
                    show_progress_bar=False,
                )
                rerank_ids = [
                    chunk_id
                    for _, chunk_id in sorted(
                        zip(rerank_scores, hybrid_ids), key=lambda value: (-float(value[0]), value[1])
                    )
                ]
                rerank_ms = (time.perf_counter() - rerank_start) * 1000
                rows_by_method = {
                    "vector": (vector_ids, embedding_ms + vector_ms),
                    "keyword": (keyword_ids, keyword_ms),
                    "hybrid": (hybrid_ids, embedding_ms + vector_ms + keyword_ms + fusion_ms),
                    "reranked": (rerank_ids, embedding_ms + vector_ms + keyword_ms + fusion_ms + rerank_ms),
                }
                for method, (ids, latency_ms) in rows_by_method.items():
                    metrics5 = metric_summary(ids, judgment, 5)
                    metrics10 = metric_summary(ids, judgment, 10)
                    measurements[method].append(
                        {
                            "query_id": query["query_id"],
                            "language": query["language"],
                            "retrieved": ids,
                            "latency_ms": latency_ms,
                            "embedding_ms": embedding_ms,
                            "vector_ms": vector_ms,
                            "keyword_ms": keyword_ms,
                            "rerank_ms": rerank_ms if method == "reranked" else 0.0,
                            **metrics5,
                            **{f"{key}10": value for key, value in metrics10.items()},
                        }
                    )
    report: dict[str, object] = {"dataset_queries": len(queries), "indexed_chunks": indexed_chunks, "methods": {}}
    for method, rows in measurements.items():
        report["methods"][method] = {}
        for language in ["ar_msa", "ar_egy", "en", "overall"]:
            selected = rows if language == "overall" else [row for row in rows if row["language"] == language]
            report["methods"][method][language] = {
                metric: statistics.fmean(row[metric] for row in selected) if selected else 0.0
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
            latencies = [float(row["latency_ms"]) for row in selected]
            report["methods"][method][language]["latency_average_ms"] = statistics.fmean(latencies) if latencies else 0.0
            report["methods"][method][language]["latency_p50_ms"] = percentile(latencies, 0.5)
            report["methods"][method][language]["latency_p95_ms"] = percentile(latencies, 0.95)
        (RESULTS / f"results_{method}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    report["model_id"] = model_id
    report["schema"] = schema
    (RESULTS / f"benchmark_report_{label}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    with (RESULTS / f"benchmark_comparison_{label}.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["method", "language", "recall", "precision", "mrr", "ndcg", "average_ms", "p50_ms", "p95_ms"])
        for method, languages in report["methods"].items():
            for language, metrics in languages.items():
                writer.writerow([method, language, metrics["recall"], metrics["precision"], metrics["mrr"], metrics["ndcg"], metrics["latency_average_ms"], metrics["latency_p50_ms"], metrics["latency_p95_ms"]])
    print(json.dumps({"report": str(RESULTS / f"benchmark_report_{label}.json"), "indexed_chunks": indexed_chunks}, indent=2))


if __name__ == "__main__":
    main()
