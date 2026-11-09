"""Small explicit registry; no model is downloaded automatically."""

from collections.abc import Callable

from .base import EmbeddingProvider
from .embedding_model import FakeEmbeddingProvider, SentenceTransformerProvider

ProviderFactory = Callable[[], EmbeddingProvider]


def get_embedding_provider(model_id: str, dimension: int = 32) -> EmbeddingProvider:
    if model_id == "fake-hash-v1":
        return FakeEmbeddingProvider(dimension=dimension, model_id=model_id)
    return SentenceTransformerProvider(model_id=model_id)
