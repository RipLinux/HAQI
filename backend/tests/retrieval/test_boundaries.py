from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.contracts.retrieval import RetrievalRequest, RetrievedChunk
from app.modules.retrieval.embeddings.model_registry import get_embedding_provider
from app.modules.retrieval.keyword_search.full_text_search import PgFullTextSearcher
from app.modules.retrieval.vector_search.store import validate_vector


def test_registry_uses_offline_fake_provider_without_model_download() -> None:
    provider = get_embedding_provider("fake-hash-v1", dimension=4)
    assert provider.model_id == "fake-hash-v1"
    assert provider.get_embedding_dimension() == 4


@pytest.mark.parametrize("top_k", [0, -1, 101])
def test_retrieval_request_rejects_invalid_top_k(top_k: int) -> None:
    with pytest.raises(ValidationError):
        RetrievalRequest(query="question", top_k=top_k)


def test_vector_validation_rejects_non_numeric_values() -> None:
    with pytest.raises(ValueError):
        validate_vector(["bad", 1.0], 2)  # type: ignore[list-item]


def test_retrieval_contract_allows_missing_optional_metadata() -> None:
    result = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        retrieval_method="keyword",
    )
    assert result.metadata == {}


def test_full_text_search_configuration_is_validated() -> None:
    searcher = PgFullTextSearcher(object(), configuration="arabic")
    assert searcher.configuration == "arabic"
    with pytest.raises(ValueError):
        PgFullTextSearcher(object(), configuration="simple;drop")
