"""Validate the synthetic retrieval dataset and create a human-review package."""

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[1]
DATA = ROOT / "data" / "evaluation" / "model_comparison"
RESULTS = ROOT / "model-evaluation" / "results"


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    chunks = read_jsonl(DATA / "synthetic_chunks.jsonl")
    queries = read_jsonl(DATA / "synthetic_queries.jsonl")
    judgments = read_jsonl(DATA / "relevance_judgments.jsonl")
    chunk_ids = [str(row["chunk_id"]) for row in chunks]
    query_ids = [str(row["query_id"]) for row in queries]
    judgment_ids = [str(row["query_id"]) for row in judgments]
    chunk_set = set(chunk_ids)
    query_set = set(query_ids)
    duplicate_chunk_ids = sorted(value for value, count in Counter(chunk_ids).items() if count > 1)
    duplicate_query_ids = sorted(value for value, count in Counter(query_ids).items() if count > 1)
    duplicate_judgments = sorted(value for value, count in Counter(judgment_ids).items() if count > 1)
    missing_query_refs = sorted(set(judgment_ids) - query_set)
    missing_chunk_refs = sorted(
        {
            str(chunk_id)
            for row in judgments
            for chunk_id in row.get("relevant_chunk_ids", [])
            if str(chunk_id) not in chunk_set
        }
    )
    invalid_grades = sorted(
        {
            float(value)
            for row in judgments
            for value in row.get("relevance", {}).values()
            if float(value) not in {0.0, 1.0, 2.0}
        }
    )
    query_map = {str(row["query_id"]): row for row in queries}
    chunk_map = {str(row["chunk_id"]): row for row in chunks}
    review_path = RESULTS / "dataset_review_sheet.csv"
    RESULTS.mkdir(parents=True, exist_ok=True)
    with review_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "query_id",
                "query",
                "language",
                "category",
                "candidate_chunk_ids",
                "candidate_chunk_texts",
                "current_grades",
                "review_status",
                "reviewer_notes",
                "corrected_relevance",
            ],
        )
        writer.writeheader()
        for judgment in judgments:
            query = query_map.get(str(judgment["query_id"]), {})
            candidate_ids = [str(value) for value in judgment.get("relevant_chunk_ids", [])]
            writer.writerow(
                {
                    "query_id": judgment["query_id"],
                    "query": query.get("query", ""),
                    "language": query.get("language", ""),
                    "category": query.get("category", ""),
                    "candidate_chunk_ids": json.dumps(candidate_ids),
                    "candidate_chunk_texts": json.dumps(
                        [chunk_map.get(value, {}).get("text", "") for value in candidate_ids],
                        ensure_ascii=False,
                    ),
                    "current_grades": json.dumps(judgment.get("relevance", {})),
                    "review_status": judgment.get("review_status", "pending_human_review"),
                    "reviewer_notes": "",
                    "corrected_relevance": "",
                }
            )
    languages = Counter(str(row.get("language", "unknown")) for row in queries)
    categories = Counter(str(row.get("category", "unknown")) for row in queries)
    empty_judgments = [str(row["query_id"]) for row in judgments if not row.get("relevant_chunk_ids")]
    report = {
        "dataset_id": "haqi-model-comparison-synthetic-v1",
        "dataset_version": "1.0.0",
        "status": "machine_generated",
        "review_status": "pending_human_review",
        "synthetic_records_are_not_official_information": True,
        "total_chunks": len(chunks),
        "total_queries": len(queries),
        "total_judgments": len(judgments),
        "queries_by_language": dict(sorted(languages.items())),
        "queries_by_category": dict(sorted(categories.items())),
        "relevant_chunks_per_query": {
            "minimum": min((len(row.get("relevant_chunk_ids", [])) for row in judgments), default=0),
            "maximum": max((len(row.get("relevant_chunk_ids", [])) for row in judgments), default=0),
            "average": (
                sum(len(row.get("relevant_chunk_ids", [])) for row in judgments) / len(judgments)
                if judgments
                else 0.0
            ),
        },
        "queries_with_no_relevant_chunks": empty_judgments,
        "duplicate_chunk_ids": duplicate_chunk_ids,
        "duplicate_query_ids": duplicate_query_ids,
        "duplicate_judgments": duplicate_judgments,
        "missing_query_references": missing_query_refs,
        "missing_chunk_references": missing_chunk_refs,
        "invalid_relevance_grades": invalid_grades,
        "human_review_completion_percent": 0.0,
        "review_sheet": str(review_path.relative_to(ROOT)),
    }
    (RESULTS / "dataset_quality_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if any(
        [
            duplicate_chunk_ids,
            duplicate_query_ids,
            duplicate_judgments,
            missing_query_refs,
            missing_chunk_refs,
            invalid_grades,
        ]
    ):
        raise SystemExit("dataset validation failed; inspect dataset_quality_report.json")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
