
from uuid import uuid4

import pytest

from app.contracts.retrieval import RetrievalMethod, RetrievalRequest, RetrievedChunk
from app.modules.retrieval.keyword_search.adapter import KeywordSearchAdapter


class FakeKeywordSearcher:
    def __init__(self) -> None:
        self.received = None

    async def search(
        self, query: str, top_k: int = 10, filters=None
    ) -> list[RetrievedChunk]:
        self.received = {
            "query": query,
            "top_k": top_k,
            "filters": filters,
        }
        return [
            RetrievedChunk(
                chunk_id=uuid4(),
                document_id=uuid4(),
                text="Keyword evidence",
                retrieval_method=RetrievalMethod.KEYWORD,
            )
        ]


@pytest.mark.asyncio
async def test_adapter_prefers_retrieval_query() -> None:
    searcher = FakeKeywordSearcher()
    adapter = KeywordSearchAdapter(searcher)

    results = await adapter(
        RetrievalRequest(
            query="Original query",
            retrieval_query="Normalized query",
            top_k=5,
        )
    )

    assert searcher.received["query"] == "Normalized query"
    assert searcher.received["top_k"] == 5
    assert len(results) == 1


@pytest.mark.asyncio
async def test_adapter_falls_back_to_original_query() -> None:
    searcher = FakeKeywordSearcher()
    adapter = KeywordSearchAdapter(searcher)

    await adapter(RetrievalRequest(query="Original query"))

    assert searcher.received["query"] == "Original query"


@pytest.mark.asyncio
async def test_adapter_passes_filters_and_top_k() -> None:
    searcher = FakeKeywordSearcher()
    adapter = KeywordSearchAdapter(searcher)

    filters = {"language": "ar"}

    await adapter(
        RetrievalRequest(
            query="HAQI",
            top_k=7,
            filters=filters,
        )
    )

    assert searcher.received["filters"] == filters
    assert searcher.received["top_k"] == 7
