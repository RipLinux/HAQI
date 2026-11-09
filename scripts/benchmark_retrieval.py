"""Summarize retrieval result JSONL files with quality and latency metrics.

The script is backend-independent: retrieval runners write one row per query
with ``query_id``, ``retrieved``, and optional ``latency_ms`` before invoking
this utility. This keeps model, PostgreSQL, and MLflow credentials out of the
offline evaluator.
"""

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

from backend.app.modules.retrieval.evaluation import (
    load_jsonl,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank_at_k,
)


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize(results_path: Path, judgments_path: Path, k: int) -> dict[str, Any]:
    results = {str(row["query_id"]): row for row in load_jsonl(results_path)}
    judgments = load_jsonl(judgments_path)
    metrics = {name: [] for name in ("recall", "precision", "mrr", "ndcg")}
    latencies: list[float] = []
    by_language: dict[str, list[float]] = {}
    for judgment in judgments:
        query_id = str(judgment["query_id"])
        row = results.get(query_id, {})
        retrieved = [str(value) for value in row.get("retrieved", [])]
        relevant = {str(value) for value in judgment.get("relevant_chunk_ids", [])}
        grades = {str(key): float(value) for key, value in judgment.get("relevance", {}).items()}
        metrics["recall"].append(recall_at_k(retrieved, relevant, k))
        metrics["precision"].append(precision_at_k(retrieved, relevant, k))
        metrics["mrr"].append(reciprocal_rank_at_k(retrieved, relevant, k))
        metrics["ndcg"].append(ndcg_at_k(retrieved, grades, k))
        if row.get("latency_ms") is not None:
            latencies.append(float(row["latency_ms"]))
        language = str(row.get("language", judgment.get("language", "unknown")))
        by_language.setdefault(language, []).append(metrics["recall"][-1])

    count = len(judgments)
    return {
        "queries": count,
        "k": k,
        "quality": {name: statistics.fmean(values) if values else 0.0 for name, values in metrics.items()},
        "latency_ms": {
            "average": statistics.fmean(latencies) if latencies else None,
            "p50": percentile(latencies, 0.50) if latencies else None,
            "p95": percentile(latencies, 0.95) if latencies else None,
            "measured_queries": len(latencies),
        },
        "recall_by_language": {
            language: statistics.fmean(values) if values else 0.0
            for language, values in sorted(by_language.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("judgments", type=Path)
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(summarize(args.results, args.judgments, args.k), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
