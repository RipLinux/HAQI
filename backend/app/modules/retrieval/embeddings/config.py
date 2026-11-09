"""Embedding configuration without importing or loading a model."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    model_id: str = "fake-hash-v1"
    dimension: int = 384
    device: str = "cpu"
    batch_size: int = 32

    @classmethod
    def from_environment(cls) -> "EmbeddingConfig":
        return cls(
            model_id=os.getenv("EMBEDDING_MODEL_ID", cls.model_id),
            dimension=int(os.getenv("EMBEDDING_DIMENSION", str(cls.dimension))),
            device=os.getenv("EMBEDDING_DEVICE", cls.device),
            batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", str(cls.batch_size))),
        )
