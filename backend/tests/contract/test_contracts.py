from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.contracts.api import ChatRequest
from app.contracts.chunks import Chunk
from app.contracts.query import UserQuery


def test_chat_request_serializes_arabic_text() -> None:
    request = ChatRequest(query=UserQuery(text="كيف أستخرج بطاقة؟"))
    assert request.model_dump()["query"]["text"] == "كيف أستخرج بطاقة؟"


def test_chunk_requires_text() -> None:
    with pytest.raises(ValidationError):
        Chunk(document_id=uuid4(), text="", chunk_index=0)


def test_query_requires_text() -> None:
    with pytest.raises(ValidationError):
        UserQuery(text="")
