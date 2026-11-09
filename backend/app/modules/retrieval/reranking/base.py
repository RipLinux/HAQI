"""Reranker protocol."""

from collections.abc import Sequence
from typing import Protocol

from app.contracts.retrieval import RetrievedChunk


class Reranker(Protocol):
    identifier: str

    def rerank(self, query: str, candidates: Sequence[RetrievedChunk]) -> list[RetrievedChunk]: ...
