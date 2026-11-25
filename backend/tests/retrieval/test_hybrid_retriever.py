
from uuid import uuid4

import pytest

from app.contracts.retrieval import RetrievalMethod, RetrievalRequest, RetrievedChunk
from app.modules.retrieval.hybrid_search.hybrid_retriever import HybridRetriever


def make_chunk(text: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        text=text,
        retrieval_method=RetrievalMethod.VECTOR,
    )


@pytest.mark.asyncio
async def test_hybrid_retriever_fuses_vector_and_keyword_results() -> None:
    shared = make_chunk("Shared evidence")
    vector_only = make_chunk("Vector evidence")
    keyword_only = make_chunk("Keyword evidence")

    async def vector_search(request: RetrievalRequest) -> list[RetrievedChunk]:
        return [shared, vector_only]

    async def keyword_search(request: RetrievalRequest) -> list[RetrievedChunk]:
        return [shared, keyword_only]

    retriever = HybridRetriever(
        vector_search,
        keyword_search,
        candidate_k=5,
    )

    results = await retriever.search(
        RetrievalRequest(query="test query", top_k=3)
    )

    assert len(results) == 3
    assert results[0].chunk_id == shared.chunk_id
    assert results[0].retrieval_method == RetrievalMethod.HYBRID
    assert [item.rank for item in results] == [1, 2, 3]


@pytest.mark.asyncio
async def test_hybrid_retriever_passes_candidate_k_to_both_searchers() -> None:
    received_top_k: list[int] = []

    async def vector_search(request: RetrievalRequest) -> list[RetrievedChunk]:
        received_top_k.append(request.top_k)
        return []

    async def keyword_search(request: RetrievalRequest) -> list[RetrievedChunk]:
        received_top_k.append(request.top_k)
        return []

    retriever = HybridRetriever(
        vector_search,
        keyword_search,
        candidate_k=7,
    )

    results = await retriever.search(
        RetrievalRequest(query="test query", top_k=2)
    )

    assert results == []
    assert received_top_k == [7, 7]


@pytest.mark.asyncio
async def test_hybrid_retriever_respects_requested_top_k() -> None:
    candidates = [make_chunk(f"Evidence {i}") for i in range(5)]

    async def vector_search(request: RetrievalRequest) -> list[RetrievedChunk]:
        return candidates

    async def keyword_search(request: RetrievalRequest) -> list[RetrievedChunk]:
        return []

    retriever = HybridRetriever(
        vector_search,
        keyword_search,
        candidate_k=5,
    )

    results = await retriever.search(
        RetrievalRequest(query="test query", top_k=2)
    )

    assert len(results) == 2
