
from uuid import uuid4

import pytest

from app.modules.retrieval.keyword_search.full_text_search import (
    PgFullTextSearcher,
)


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows):
        self.rows = rows
        self.executed_params = None
        self.executed_statement = None

    async def execute(self, statement, params=None):
        self.executed_statement = statement
        self.executed_params = params
        return FakeResult(self.rows)


@pytest.mark.asyncio
async def test_full_text_search_passes_query_and_top_k():
    chunk_id = uuid4()
    document_id = uuid4()

    session = FakeSession([
        (chunk_id, document_id, "Test chunk", "https://example.com", 0.8)
    ])

    searcher = PgFullTextSearcher(session)

    results = await searcher.search("test query", top_k=5)

    assert session.executed_params == {
        "query": "test query",
        "top_k": 5,
    }

    assert len(results) == 1
    assert results[0].chunk_id == chunk_id
    assert results[0].document_id == document_id
    assert results[0].text == "Test chunk"
    assert results[0].source_url == "https://example.com"
    assert results[0].score == 0.8
