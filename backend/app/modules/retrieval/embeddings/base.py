"""Embedding provider protocols."""

from collections.abc import Sequence
from typing import Protocol


class EmbeddingProvider(Protocol):
    """Provider boundary kept independent from any model framework."""

    model_id: str

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...

    def get_embedding_dimension(self) -> int: ...
