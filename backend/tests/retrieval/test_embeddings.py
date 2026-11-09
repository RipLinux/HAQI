from math import isclose, sqrt

import pytest

from app.modules.retrieval.embeddings.embedding_model import FakeEmbeddingProvider


def test_fake_provider_is_deterministic_and_normalized() -> None:
    provider = FakeEmbeddingProvider(dimension=8)
    first = provider.embed_query("كيف أستخرج بطاقة؟")
    second = provider.embed_query("كيف أستخرج بطاقة؟")
    assert first == second
    assert isclose(sqrt(sum(value * value for value in first)), 1.0)


def test_fake_provider_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        FakeEmbeddingProvider().embed_query(" ")
