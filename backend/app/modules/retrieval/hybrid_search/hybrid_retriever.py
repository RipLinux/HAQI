"""Composable hybrid retrieval pipeline."""

import asyncio
from collections.abc import Awaitable, Callable

from app.contracts.retrieval import RetrievalRequest, RetrievedChunk

from .fusion import reciprocal_rank_fusion

SearchFn = Callable[[RetrievalRequest], Awaitable[list[RetrievedChunk]]]


class HybridRetriever:
    def __init__(
        self,
        vector_search: SearchFn,
        keyword_search: SearchFn,
        *,
        fusion_constant: int = 60,
        candidate_k: int = 20,
    ) -> None:
        self.vector_search = vector_search
        self.keyword_search = keyword_search
        self.fusion_constant = fusion_constant
        self.candidate_k = candidate_k

    async def search(self, request: RetrievalRequest) -> list[RetrievedChunk]:
        candidate_request = request.model_copy(update={"top_k": self.candidate_k})
        vector_results, keyword_results = await _gather(
            self.vector_search(candidate_request),
            self.keyword_search(candidate_request),
        )
        return reciprocal_rank_fusion(
            [vector_results, keyword_results],
            fusion_constant=self.fusion_constant,
            top_k=request.top_k,
        )


async def _gather(
    first: Awaitable[list[RetrievedChunk]], second: Awaitable[list[RetrievedChunk]]
) -> tuple[list[RetrievedChunk], list[RetrievedChunk]]:
    return await asyncio.gather(first, second)
