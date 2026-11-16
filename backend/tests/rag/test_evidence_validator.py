
import pytest

from app.modules.rag.context_builder import ContextBuilder
from app.modules.rag.evidence_validator import EvidenceValidator
from app.contracts.retrieval import RetrievedChunk


@pytest.fixture
def context():
    chunks = [
        RetrievedChunk(
            chunk_id="11111111-1111-4111-8111-111111111111",
            document_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            text="National ID is required.",
            source_url="https://example.gov.eg/id",
            retrieval_method="hybrid",
        ),
        RetrievedChunk(
            chunk_id="22222222-2222-4222-8222-222222222222",
            document_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
            text="Applications are submitted online.",
            source_url="https://example.gov.eg/apply",
            retrieval_method="hybrid",
        ),
    ]

    return ContextBuilder().build(chunks)


def test_validates_single_evidence_reference(context):
    result = EvidenceValidator().validate(
        "A national ID is required [E1].",
        context,
    )

    assert result.valid is True
    assert result.answer.abstained is False
    assert len(result.answer.citations) == 1
    assert str(result.answer.citations[0].chunk_id) == (
        "11111111-1111-4111-8111-111111111111"
    )


def test_validates_multiple_references(context):
    result = EvidenceValidator().validate(
        "An ID is required [E1]. Apply online [E2].",
        context,
    )

    assert result.valid is True
    assert len(result.answer.citations) == 2


def test_deduplicates_repeated_references(context):
    result = EvidenceValidator().validate(
        "An ID is required [E1]. The ID is mandatory [E1].",
        context,
    )

    assert result.valid is True
    assert len(result.answer.citations) == 1


def test_rejects_unknown_reference(context):
    result = EvidenceValidator().validate(
        "This is required [E99].",
        context,
    )

    assert result.valid is False
    assert result.answer.abstained is True
    assert result.answer.citations == []


def test_rejects_answer_without_references(context):
    result = EvidenceValidator().validate(
        "A national ID is required.",
        context,
    )

    assert result.valid is False
    assert result.answer.abstained is True


def test_rejects_empty_answer(context):
    result = EvidenceValidator().validate("", context)

    assert result.valid is False
    assert result.answer.abstained is True


def test_rejects_empty_context():
    empty_context = ContextBuilder().build([])

    result = EvidenceValidator().validate(
        "A national ID is required [E1].",
        empty_context,
    )

    assert result.valid is False
    assert result.answer.abstained is True


def test_citation_uses_original_source_url(context):
    result = EvidenceValidator().validate(
        "Apply online [E2].",
        context,
    )

    assert result.answer.citations[0].source_url == (
        "https://example.gov.eg/apply"
    )
