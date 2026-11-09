"""Embedding validation and batch indexing orchestration."""

from collections.abc import Mapping, Sequence
from typing import Any

from .store import VectorStore


async def index_chunks(
    store: VectorStore, rows: Sequence[Mapping[str, Any]], expected_dimension: int
) -> None:
    """Validate dimensions before delegating writes to the shared storage adapter."""

    for row in rows:
        embedding = row.get("embedding")
        if embedding is None or len(embedding) != expected_dimension:
            raise ValueError("Every indexed row must contain the configured vector dimension")
    await store.add_embeddings(rows)
