"""Lazy embedding providers.

The real Sentence Transformers provider is intentionally optional. Importing this
module never downloads or initializes a model.
"""

import hashlib
import importlib
import math
from collections.abc import Sequence
from typing import Any


def _validate_texts(texts: Sequence[str]) -> None:
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Embedding inputs must contain non-empty strings")


class FakeEmbeddingProvider:
    """Deterministic, offline provider for unit tests and local plumbing."""

    def __init__(self, dimension: int = 32, model_id: str = "fake-hash-v1") -> None:
        if dimension < 1:
            raise ValueError("Embedding dimension must be positive")
        self.dimension = dimension
        self.model_id = model_id

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        _validate_texts(texts)
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        _validate_texts([text])
        return self._embed(text)

    def get_embedding_dimension(self) -> int:
        return self.dimension

    def _embed(self, text: str) -> list[float]:
        vector: list[float] = []
        for index in range(self.dimension):
            digest = hashlib.sha256(f"{index}:{text}".encode()).digest()
            vector.append((int.from_bytes(digest[:8], "big") / 2**64) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector]


class SentenceTransformerProvider:
    """Lazy adapter for an explicitly selected Sentence Transformers model."""

    def __init__(self, model_id: str, device: str = "cpu") -> None:
        self.model_id = model_id
        self.device = device
        self._model: Any | None = None

    def _get_model(self) -> Any:
        if self._model is None:
            try:
                sentence_transformers = importlib.import_module("sentence_transformers")
            except ImportError as exc:
                raise RuntimeError(
                    "Install the optional sentence-transformers dependency to use this provider"
                ) from exc
            self._model = sentence_transformers.SentenceTransformer(
                self.model_id, device=self.device
            )
        return self._model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        _validate_texts(texts)
        vectors = self._get_model().encode(list(texts), convert_to_numpy=False)
        return [[float(value) for value in vector] for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def get_embedding_dimension(self) -> int:
        return int(self._get_model().get_sentence_embedding_dimension())
