
"""Adapter between retrieval requests and PostgreSQL keyword search."""

from collections.abc import Mapping
from typing import Protocol

from app.contracts.retrieval import RetrievalRequest, RetrievedChunk


class KeywordSearchBackend(Protocol):
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Mapping[str, str] | None = None,
    ) -> list[RetrievedChunk]:
        ...


class KeywordSearchAdapter:
    """Adapt the keyword search interface to the hybrid retriever contract."""

    def __init__(self, searcher: KeywordSearchBackend) -> None:
        self.searcher = searcher

    async def __call__(
        self, request: RetrievalRequest
    ) -> list[RetrievedChunk]:
        query = request.retrieval_query or request.query

        return await self.searcher.search(
            query=query,
            top_k=request.top_k,
            filters=request.filters,
        )
