"""Evaluate a retrieval result JSONL file against a judgment JSONL file.

This offline utility deliberately accepts result IDs rather than connecting to a
database, so it can be used with synthetic or reviewed benchmark outputs.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from backend.app.modules.retrieval.evaluation import (
    load_jsonl,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank_at_k,
)


def evaluate(results_path: Path, judgments_path: Path, k: int) -> dict[str, object]:
    results = {str(row["query_id"]): row for row in load_jsonl(results_path)}
    judgments = load_jsonl(judgments_path)
    values = {"recall": [], "precision": [], "mrr": [], "ndcg": []}
    for judgment in judgments:
        query_id = str(judgment["query_id"])
        retrieved = [str(chunk_id) for chunk_id in results.get(query_id, {}).get("retrieved", [])]
        relevant = {str(chunk_id) for chunk_id in judgment.get("relevant_chunk_ids", [])}
        grades = {str(key): float(value) for key, value in judgment.get("relevance", {}).items()}
        values["recall"].append(recall_at_k(retrieved, relevant, k))
        values["precision"].append(precision_at_k(retrieved, relevant, k))
        values["mrr"].append(reciprocal_rank_at_k(retrieved, relevant, k))
        values["ndcg"].append(ndcg_at_k(retrieved, grades, k))
    count = len(judgments)
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "queries": count,
        "k": k,
        "macro_average": {
            metric: sum(scores) / count if count else 0.0 for metric, scores in values.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("judgments", type=Path)
    parser.add_argument("-k", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.results, args.judgments, args.k), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
