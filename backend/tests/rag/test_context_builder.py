
from uuid import uuid4

import pytest

from app.contracts.retrieval import RetrievedChunk
from app.modules.rag.context_builder import ContextBuilder


def make_chunk(
    text: str | None,
    source_url: str | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        text=text,
        source_url=source_url,
        retrieval_method="hybrid",
    )


def test_build_formats_evidence_with_source() -> None:
    chunk = make_chunk("Eligibility requirements", "https://example.gov.eg")

    result = ContextBuilder().build([chunk])

    assert "[E1]" in result.context_text
    assert "Eligibility requirements" in result.context_text
    assert "https://example.gov.eg" in result.context_text
    assert result.chunks == (chunk,)


def test_build_skips_empty_chunks() -> None:
    empty = make_chunk("   ")
    valid = make_chunk("Valid evidence")

    result = ContextBuilder().build([empty, valid])

    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == valid.chunk_id
    assert "[E1]" in result.context_text
    assert "[E2]" not in result.context_text


def test_build_removes_duplicate_chunks() -> None:
    chunk = make_chunk("Same evidence")

    result = ContextBuilder().build([chunk, chunk])

    assert len(result.chunks) == 1


def test_build_respects_max_chunks() -> None:
    chunks = [make_chunk(f"Evidence {i}") for i in range(5)]

    result = ContextBuilder(max_chunks=2).build(chunks)

    assert len(result.chunks) == 2
    assert "Evidence 0" in result.context_text
    assert "Evidence 1" in result.context_text
    assert "Evidence 2" not in result.context_text


def test_builder_rejects_invalid_max_chunks() -> None:
    with pytest.raises(ValueError):
        ContextBuilder(max_chunks=0)


def test_build_returns_empty_result_for_no_evidence() -> None:
    result = ContextBuilder().build([])

    assert result.context_text == ""
    assert result.chunks == ()
