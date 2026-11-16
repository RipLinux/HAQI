
from uuid import uuid4

import pytest

from app.contracts.retrieval import RetrievalMethod, RetrievedChunk
from app.modules.retrieval.reranking.reranker import (
    CrossEncoderReranker,
    NoOpReranker,
)


class FakeCrossEncoder:
    def __init__(self, scores: list[float]) -> None:
        self.scores = scores
        self.received_pairs = None

    def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        self.received_pairs = pairs
        return self.scores


def make_chunk(text: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        text=text,
        retrieval_method=RetrievalMethod.HYBRID,
    )


def test_noop_reranker_is_explicit_and_handles_empty_candidates() -> None:
    reranker = NoOpReranker()

    assert reranker.identifier == "none"
    assert reranker.rerank("query", []) == []


def test_cross_encoder_reranker_sorts_by_descending_score() -> None:
    reranker = CrossEncoderReranker(model_id="fake-model")
    fake_model = FakeCrossEncoder([0.2, 0.9, 0.5])
    reranker._model = fake_model

    candidates = [
        make_chunk("First document"),
        make_chunk("Second document"),
        make_chunk("Third document"),
    ]

    results = reranker.rerank("test query", candidates)

    assert [item.text for item in results] == [
        "Second document",
        "Third document",
        "First document",
    ]
    assert [item.score for item in results] == [0.9, 0.5, 0.2]
    assert [item.rank for item in results] == [1, 2, 3]
    assert all(
        item.retrieval_method == RetrievalMethod.RERANKED
        for item in results
    )


def test_cross_encoder_reranker_passes_query_and_candidate_text() -> None:
    reranker = CrossEncoderReranker(model_id="fake-model")
    fake_model = FakeCrossEncoder([0.8])
    reranker._model = fake_model

    reranker.rerank("HAQI query", [make_chunk("Evidence text")])

    assert fake_model.received_pairs == [
        ("HAQI query", "Evidence text")
    ]


def test_cross_encoder_reranker_handles_empty_candidates() -> None:
    reranker = CrossEncoderReranker(model_id="fake-model")

    assert reranker.rerank("query", []) == []
    assert reranker._model is None


def test_cross_encoder_reranker_rejects_mismatched_score_count() -> None:
    reranker = CrossEncoderReranker(model_id="fake-model")
    reranker._model = FakeCrossEncoder([0.9])

    candidates = [
        make_chunk("First document"),
        make_chunk("Second document"),
    ]

    with pytest.raises(ValueError):
        reranker.rerank("query", candidates)
