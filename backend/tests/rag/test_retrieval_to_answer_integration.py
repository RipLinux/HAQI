from uuid import uuid4

import pytest

from app.contracts.query import UserQuery
from app.contracts.retrieval import RetrievalRequest, RetrievedChunk
from app.modules.rag.answer_generator import AnswerGenerator
from app.modules.rag.context_builder import ContextBuilder
from app.modules.rag.evidence_validator import EvidenceValidator
from app.modules.rag.llm import MockLLMProvider
from app.modules.retrieval.hybrid_search.hybrid_retriever import HybridRetriever


@pytest.mark.asyncio
async def test_hybrid_retrieval_to_grounded_answer():
    shared_chunk = RetrievedChunk(
        chunk_id="11111111-1111-4111-8111-111111111111",
        document_id="22222222-2222-4222-8222-222222222222",
        text="A national ID is required to apply for this service.",
        source_url="https://example.gov.eg/service",
        retrieval_method="vector",
    )

    vector_only_chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        text="Vector-specific supporting information.",
        source_url="https://example.gov.eg/vector",
        retrieval_method="vector",
    )

    keyword_only_chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        text="Keyword-specific supporting information.",
        source_url="https://example.gov.eg/keyword",
        retrieval_method="keyword",
    )

    calls = {"vector": 0, "keyword": 0}

    async def vector_search(request):
        calls["vector"] += 1
        return [shared_chunk, vector_only_chunk]

    async def keyword_search(request):
        calls["keyword"] += 1
        return [shared_chunk, keyword_only_chunk]

    retriever = HybridRetriever(
        vector_search,
        keyword_search,
        candidate_k=5,
    )

    request = RetrievalRequest(
        query="What document is required?",
        top_k=3,
    )

    retrieved_chunks = await retriever.search(request)

    assert calls == {"vector": 1, "keyword": 1}
    assert len(retrieved_chunks) == 3
    assert retrieved_chunks[0].chunk_id == shared_chunk.chunk_id

    context = ContextBuilder().build(retrieved_chunks)

    assert len(context.chunks) == 3
    assert "A national ID is required" in context.context_text

    provider = MockLLMProvider(
        response="A national ID is required [E1]."
    )

    generator = AnswerGenerator(provider=provider)

    generated_answer = generator.generate(
        UserQuery(text="What document is required?"),
        context,
    )

    assert "A national ID is required" in provider.last_user_prompt

    validation = EvidenceValidator().validate(
        generated_answer,
        context,
    )

    assert validation.valid is True
    assert validation.answer.abstained is False
    assert len(validation.answer.citations) == 1
    assert validation.answer.citations[0].chunk_id == shared_chunk.chunk_id
    assert validation.answer.citations[0].source_url == (
        "https://example.gov.eg/service"
    )

