
"""Tests for the embedding indexing orchestration."""

from uuid import uuid4

import pytest

from app.contracts.chunks import Chunk
from app.contracts.common import Metadata
from app.modules.retrieval.vector_search.indexer import index_chunks


class FakeEmbeddingProvider:
    model_id = "fake-test-model"

    def __init__(self, vectors):
        self.vectors = vectors
        self.received_texts = None

    def embed_documents(self, texts):
        self.received_texts = list(texts)
        return self.vectors

    def embed_query(self, text):
        return self.vectors[0]

    def get_embedding_dimension(self):
        return 3


class FakeVectorStore:
    def __init__(self):
        self.received_rows = None
        self.calls = 0

    async def add_embeddings(self, rows):
        self.calls += 1
        self.received_rows = list(rows)


def make_chunk(text, source_url=None):
    return Chunk(
        document_id=uuid4(),
        text=text,
        chunk_index=0,
        metadata=Metadata(source_url=source_url),
    )


@pytest.mark.asyncio
async def test_index_chunks_generates_and_stores_embeddings():
    chunks = [
        make_chunk("First chunk", "https://example.com/1"),
        make_chunk("Second chunk", "https://example.com/2"),
    ]

    vectors = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    provider = FakeEmbeddingProvider(vectors)
    store = FakeVectorStore()

    result = await index_chunks(store, provider, chunks)

    assert result == 2
    assert provider.received_texts == ["First chunk", "Second chunk"]
    assert store.calls == 1
    assert len(store.received_rows) == 2

    for chunk, row in zip(chunks, store.received_rows, strict=True):
        assert row["chunk_id"] == chunk.id
        assert row["document_id"] == chunk.document_id
        assert row["text"] == chunk.text

    assert store.received_rows[0]["source_url"] == "https://example.com/1"
    assert store.received_rows[1]["source_url"] == "https://example.com/2"


@pytest.mark.asyncio
async def test_index_chunks_returns_zero_for_empty_input():
    provider = FakeEmbeddingProvider([])
    store = FakeVectorStore()

    result = await index_chunks(store, provider, [])

    assert result == 0
    assert provider.received_texts is None
    assert store.calls == 0


@pytest.mark.asyncio
async def test_index_chunks_rejects_wrong_number_of_vectors():
    chunks = [
        make_chunk("First chunk"),
        make_chunk("Second chunk"),
    ]

    provider = FakeEmbeddingProvider([[0.1, 0.2, 0.3]])
    store = FakeVectorStore()

    with pytest.raises(ValueError, match="one vector per chunk"):
        await index_chunks(store, provider, chunks)

    assert store.calls == 0


@pytest.mark.asyncio
async def test_index_chunks_rejects_wrong_vector_dimension():
    chunks = [make_chunk("First chunk")]

    provider = FakeEmbeddingProvider([[0.1, 0.2]])
    store = FakeVectorStore()

    with pytest.raises(ValueError, match="Vector dimension mismatch"):
        await index_chunks(store, provider, chunks)

    assert store.calls == 0


@pytest.mark.asyncio
async def test_index_chunks_preserves_missing_source_url():
    chunks = [make_chunk("Chunk without source URL")]

    provider = FakeEmbeddingProvider([[0.1, 0.2, 0.3]])
    store = FakeVectorStore()

    await index_chunks(store, provider, chunks)

    assert store.received_rows[0]["source_url"] is None
