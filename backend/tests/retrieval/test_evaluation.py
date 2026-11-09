from app.modules.retrieval.evaluation import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank_at_k,
)


def test_metrics_are_calculated_at_k() -> None:
    retrieved = ["a", "b", "c"]
    relevant = {"b", "c"}
    assert recall_at_k(retrieved, relevant, 2) == 0.5
    assert precision_at_k(retrieved, relevant, 2) == 0.5
    assert reciprocal_rank_at_k(retrieved, relevant, 2) == 0.5
    assert ndcg_at_k(retrieved, {"b": 2, "c": 1}, 2) > 0


def test_metrics_return_zero_without_relevance() -> None:
    assert recall_at_k(["a"], set(), 1) == 0
    assert reciprocal_rank_at_k(["a"], set(), 1) == 0
    assert ndcg_at_k(["a"], {}, 1) == 0
