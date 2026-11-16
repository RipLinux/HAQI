
from uuid import uuid4

from app.contracts.query import UserQuery
from app.contracts.retrieval import RetrievedChunk
from app.modules.rag.context_builder import ContextBuilder
from app.modules.rag.prompt_builder import PromptBuilder


def make_chunk(text: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        text=text,
        source_url="https://example.gov.eg",
        retrieval_method="hybrid",
    )


def test_build_includes_user_question() -> None:
    query = UserQuery(text="ما شروط استخراج البطاقة؟")
    context = ContextBuilder().build([make_chunk("Official requirements")])

    result = PromptBuilder().build(query, context)

    assert "ما شروط استخراج البطاقة؟" in result.user_prompt


def test_build_includes_retrieved_evidence() -> None:
    query = UserQuery(text="What are the requirements?")
    context = ContextBuilder().build([make_chunk("Official requirements")])

    result = PromptBuilder().build(query, context)

    assert "Official requirements" in result.user_prompt
    assert "[E1]" in result.user_prompt


def test_build_includes_grounding_instructions() -> None:
    query = UserQuery(text="What are the requirements?")
    context = ContextBuilder().build([make_chunk("Some evidence")])

    result = PromptBuilder().build(query, context)

    assert "Never invent facts" in result.system_prompt
    assert "evidence" in result.system_prompt.lower()


def test_build_includes_safe_abstention_rules() -> None:
    query = UserQuery(text="Unknown service")
    context = ContextBuilder().build([])

    result = PromptBuilder().build(query, context)

    assert "insufficient" in result.system_prompt.lower()
    assert "No evidence was retrieved" in result.user_prompt


def test_build_includes_security_instructions() -> None:
    query = UserQuery(text="Explain this service")
    context = ContextBuilder().build([make_chunk("Some evidence")])

    result = PromptBuilder().build(query, context)

    assert "untrusted reference data" in result.system_prompt


def test_build_includes_language_metadata() -> None:
    query = UserQuery(text="Explain this service", language="en")
    context = ContextBuilder().build([])

    result = PromptBuilder().build(query, context)

    assert "USER LANGUAGE METADATA: en" in result.user_prompt


def test_prompt_builder_does_not_modify_context() -> None:
    query = UserQuery(text="Explain this service")
    chunk = make_chunk("Some evidence")
    context = ContextBuilder().build([chunk])

    original_context = context.context_text

    PromptBuilder().build(query, context)

    assert context.context_text == original_context
    assert context.chunks == (chunk,)
