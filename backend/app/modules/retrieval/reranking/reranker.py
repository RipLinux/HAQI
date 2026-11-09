"""Explicit no-op reranker and optional lazy cross-encoder adapter."""

import importlib
from collections.abc import Sequence
from typing import Any

from app.contracts.retrieval import RetrievalMethod, RetrievedChunk


class NoOpReranker:
    identifier = "none"

    def rerank(self, query: str, candidates: Sequence[RetrievedChunk]) -> list[RetrievedChunk]:
        _ = query
        return [
            candidate.model_copy(
                update={"rank": rank, "retrieval_method": RetrievalMethod.RERANKED}
            )
            for rank, candidate in enumerate(candidates, start=1)
        ]


class CrossEncoderReranker:
    """Lazy optional adapter; model scores must be evaluated before production use."""

    def __init__(self, model_id: str, device: str = "cpu") -> None:
        self.identifier = model_id
        self.device = device
        self._model: Any | None = None

    def _get_model(self) -> Any:
        if self._model is None:
            try:
                sentence_transformers = importlib.import_module("sentence_transformers")
            except ImportError as exc:
                raise RuntimeError(
                    "Install sentence-transformers to use the CrossEncoder reranker"
                ) from exc
            self._model = sentence_transformers.CrossEncoder(self.identifier, device=self.device)
        return self._model

    def rerank(self, query: str, candidates: Sequence[RetrievedChunk]) -> list[RetrievedChunk]:
        if not candidates:
            return []
        pairs = [(query, candidate.text or "") for candidate in candidates]
        scores = self._get_model().predict(pairs)
        ranked = sorted(
            zip(candidates, scores, strict=True),
            key=lambda item: (-float(item[1]), str(item[0].chunk_id)),
        )
        return [
            candidate.model_copy(
                update={
                    "score": float(score),
                    "rank": rank,
                    "retrieval_method": RetrievalMethod.RERANKED,
                }
            )
            for rank, (candidate, score) in enumerate(ranked, start=1)
        ]
