
import pytest

from app.contracts.query import UserQuery
from app.contracts.retrieval import RetrievedChunk
from app.modules.rag.answer_generator import AnswerGenerator
from app.modules.rag.context_builder import ContextBuilder
from app.modules.rag.llm import MockLLMProvider


def make_context():
    chunk = RetrievedChunk(
        chunk_id="11111111-1111-4111-8111-111111111111",
        document_id="22222222-2222-4222-8222-222222222222",
        text="Official service requirements.",
        source_url="https://example.gov.eg",
        retrieval_method="hybrid",
    )

    return ContextBuilder().build([chunk])


def test_generator_returns_provider_response() -> None:
    provider = MockLLMProvider(response="Generated HAQI answer")
    generator = AnswerGenerator(provider=provider)

    result = generator.generate(
        UserQuery(text="What are the requirements?"),
        make_context(),
    )

    assert result == "Generated HAQI answer"


def test_generator_passes_system_prompt_to_provider() -> None:
    provider = MockLLMProvider()
    generator = AnswerGenerator(provider=provider)

    generator.generate(
        UserQuery(text="Explain this service"),
        make_context(),
    )

    assert provider.last_system_prompt is not None
    assert "Never invent facts" in provider.last_system_prompt


def test_generator_passes_question_and_evidence() -> None:
    provider = MockLLMProvider()
    generator = AnswerGenerator(provider=provider)

    generator.generate(
        UserQuery(text="What are the requirements?"),
        make_context(),
    )

    assert provider.last_user_prompt is not None
    assert "What are the requirements?" in provider.last_user_prompt
    assert "Official service requirements." in provider.last_user_prompt


def test_generator_supports_empty_context() -> None:
    provider = MockLLMProvider(response="Insufficient evidence.")
    generator = AnswerGenerator(provider=provider)

    result = generator.generate(
        UserQuery(text="Unknown service"),
        ContextBuilder().build([]),
    )

    assert result == "Insufficient evidence."
    assert "No evidence was retrieved" in provider.last_user_prompt


def test_generator_rejects_empty_provider_response() -> None:
    provider = MockLLMProvider(response="   ")
    generator = AnswerGenerator(provider=provider)

    with pytest.raises(RuntimeError, match="empty or invalid"):
        generator.generate(
            UserQuery(text="Explain this service"),
            make_context(),
        )
