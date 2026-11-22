
"""Embedding generation and batch indexing orchestration."""

from collections.abc import Sequence

from app.contracts.chunks import Chunk
from app.modules.retrieval.embeddings.base import EmbeddingProvider

from .store import VectorStore, validate_vector


async def index_chunks(
    store: VectorStore,
    provider: EmbeddingProvider,
    chunks: Sequence[Chunk],
) -> int:
    """Generate embeddings and index chunks in a single batch."""

    if not chunks:
        return 0

    texts = [chunk.text for chunk in chunks]

    vectors = provider.embed_documents(texts)

    if len(vectors) != len(chunks):
        raise ValueError(
            "The embedding provider must return one vector per chunk"
        )

    expected_dimension = provider.get_embedding_dimension()

    rows = []

    for chunk, vector in zip(chunks, vectors, strict=True):
        validated_vector = validate_vector(vector, expected_dimension)

        rows.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "text": chunk.text,
                "embedding": validated_vector,
                "source_url": chunk.metadata.source_url,
            }
        )

    await store.add_embeddings(rows)

    return len(rows)
