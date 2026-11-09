"""Reciprocal Rank Fusion utilities."""

from collections.abc import Iterable

from app.contracts.retrieval import RetrievalMethod, RetrievedChunk


def reciprocal_rank_fusion(
    result_lists: Iterable[Iterable[RetrievedChunk]],
    *,
    fusion_constant: int = 60,
    top_k: int = 10,
) -> list[RetrievedChunk]:
    if fusion_constant < 1 or top_k < 1:
        raise ValueError("fusion_constant and top_k must be positive")
    merged: dict[str, RetrievedChunk] = {}
    scores: dict[str, float] = {}
    for results in result_lists:
        for rank, result in enumerate(results, start=1):
            key = str(result.chunk_id)
            scores[key] = scores.get(key, 0.0) + 1 / (fusion_constant + rank)
            merged.setdefault(key, result)
    ordered = sorted(merged, key=lambda key: (-scores[key], key))
    return [
        merged[key].model_copy(
            update={
                "score": scores[key],
                "rank": rank,
                "retrieval_method": RetrievalMethod.HYBRID,
            }
        )
        for rank, key in enumerate(ordered[:top_k], start=1)
    ]
