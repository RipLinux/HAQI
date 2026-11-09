"""Offline retrieval metrics and JSONL evaluation loading."""

import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


def recall_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def precision_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if k < 1:
        raise ValueError("k must be positive")
    return len(set(retrieved[:k]) & relevant) / k


def reciprocal_rank_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    for rank, chunk_id in enumerate(retrieved[:k], start=1):
        if chunk_id in relevant:
            return 1 / rank
    return 0.0


def ndcg_at_k(retrieved: Sequence[str], relevance: Mapping[str, float], k: int) -> float:
    import math

    def dcg(values: Iterable[float]) -> float:
        return sum((2**value - 1) / math.log2(rank + 2) for rank, value in enumerate(values))

    actual = dcg(relevance.get(chunk_id, 0.0) for chunk_id in retrieved[:k])
    ideal = dcg(sorted(relevance.values(), reverse=True)[:k])
    return actual / ideal if ideal else 0.0


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]
