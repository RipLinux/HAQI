from app.contracts.query import UserQuery
from app.contracts.retrieval import RetrievedChunk
from app.modules.rag.answer_generator import AnswerGenerator
from app.modules.rag.context_builder import ContextBuilder
from app.modules.rag.evidence_validator import EvidenceValidator
from app.modules.rag.llm import MockLLMProvider


def build_test_context():
    chunk = RetrievedChunk(
        chunk_id="11111111-1111-4111-8111-111111111111",
        document_id="22222222-2222-4222-8222-222222222222",
        text="A national ID is required to apply for this service.",
        source_url="https://example.gov.eg/service",
        retrieval_method="hybrid",
    )
    return ContextBuilder().build([chunk])


def run_pipeline(mock_response):
    provider = MockLLMProvider(response=mock_response)
    generator = AnswerGenerator(provider=provider)
    validator = EvidenceValidator()

    query = UserQuery(text="What document is required?")
    context = build_test_context()

    generated_text = generator.generate(query, context)
    validation = validator.validate(generated_text, context)

    return provider, generated_text, validation


def test_pipeline_accepts_valid_evidence_reference():
    _, generated_text, result = run_pipeline(
        "A national ID is required [E1]."
    )

    assert generated_text == "A national ID is required [E1]."
    assert result.valid is True
    assert result.answer.abstained is False
    assert len(result.answer.citations) == 1
    assert str(result.answer.citations[0].chunk_id) == (
        "11111111-1111-4111-8111-111111111111"
    )
    assert result.answer.citations[0].source_url == (
        "https://example.gov.eg/service"
    )


def test_pipeline_rejects_unknown_evidence_reference():
    _, _, result = run_pipeline(
        "A national ID is required [E99]."
    )

    assert result.valid is False
    assert result.answer.abstained is True
    assert result.answer.citations == []
    assert result.invalid_evidence_ids == ("E99",)


def test_pipeline_abstains_when_answer_has_no_citation():
    _, _, result = run_pipeline(
        "A national ID is required."
    )

    assert result.valid is False
    assert result.answer.abstained is True
    assert result.answer.citations == []
