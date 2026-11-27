"""Integration coverage for the active legacy chat endpoint and RAG service."""

import logging
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.schemas import ChatRequest, EvidenceValidationReport, NLPAnalysisResult
from app.services import rag_service as rag_service_module
from app.services.rag_service import RAGOrchestratorService
from main import app


QUESTION = "What is required to renew a national ID?"


class StubLLMProvider:
    """Deterministic provider double that never makes a network request."""

    def __init__(
        self,
        response: Any = "submitting the previous card is required [E1].",
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error

    def generate(self, system_prompt: str, user_prompt: str) -> Any:
        if self.error is not None:
            raise self.error
        return self.response


class FakeAPIError(Exception):
    """Stand-in for an upstream LLM API exception."""


@pytest.fixture
def active_rag(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[RAGOrchestratorService, dict[str, Any], Any]:
    """Isolate the active orchestrator from DB, NLP, and retrieval services."""

    chunk = {
        "chunk_id": "test-chunk-1",
        "document_id": "test-document-1",
        "chunk_text": "Submitting the previous card is required for renewal.",
        "doc_code": "TEST-NID-1",
        "doc_title": "National ID renewal guide",
        "authority": "Civil Status Authority",
        "original_url": "https://digital.gov.eg/services/national-id",
        "last_updated": "2026-01-15",
        "verification_date": "2026-02-01",
        "version": "1.0",
        "service_name_ar": "Renew national ID",
        "steps": ["Submit the previous card"],
        "required_documents": ["previous card"],
        "fees_text": "50 pounds",
        "processing_time": "7 days",
        "rerank_score": 0.95,
    }
    nlp_result = NLPAnalysisResult(
        original_text=QUESTION,
        normalized_text=QUESTION,
        extracted_intent="national_id_application",
        extracted_intent_ar="National ID service",
        sub_type="renewal",
        structured_search_query=QUESTION,
    )
    sufficient_report = EvidenceValidationReport(
        is_sufficient=True,
        decision_path="path_1_verified_context",
        source_identity_verified=True,
        relevance_passed=True,
        max_relevance_score=0.95,
        grounding_score=1.0,
        freshness_status="verified_up_to_date",
    )
    original_evidence_validator = (
        rag_service_module.evidence_validator.validate_evidence
    )

    db_manager = rag_service_module.db_manager
    monkeypatch.setattr(
        db_manager,
        "get_or_create_session",
        lambda **kwargs: {
            "session_id": kwargs.get("session_id") or "test-session",
            "pending_intent": None,
            "awaiting_clarification": False,
            "last_intent": None,
            "last_sub_type": None,
        },
    )
    monkeypatch.setattr(db_manager, "log_chat_message", lambda **kwargs: None)
    monkeypatch.setattr(
        db_manager, "update_session_clarification", lambda **kwargs: None
    )
    monkeypatch.setattr(db_manager, "set_session_context", lambda **kwargs: None)
    monkeypatch.setattr(
        rag_service_module.nlp_service,
        "analyze_query",
        lambda **kwargs: nlp_result,
    )
    monkeypatch.setattr(
        rag_service_module.retrieval_service,
        "retrieve_and_rerank",
        lambda **kwargs: [chunk],
    )
    monkeypatch.setattr(
        rag_service_module.evidence_validator,
        "validate_evidence",
        lambda **kwargs: sufficient_report,
    )

    return RAGOrchestratorService(), chunk, original_evidence_validator


def set_provider(
    monkeypatch: pytest.MonkeyPatch,
    provider: StubLLMProvider,
) -> None:
    monkeypatch.setattr(
        rag_service_module,
        "create_llm_provider",
        lambda: provider,
    )


def assert_deterministic_legacy_answer(
    service: RAGOrchestratorService,
    response,
) -> None:
    assert response.decision_type == "answered"
    assert response.answer == service._format_arabic_answer(
        response.structured_guidance,
        response.focus,
    )


def test_chat_endpoint_returns_grounded_llm_answer_and_compatible_citation(
    active_rag,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, chunk, _ = active_rag
    set_provider(monkeypatch, StubLLMProvider())

    response = TestClient(app).post(
        "/api/v1/chat",
        json={"question": QUESTION, "user_id": "rag-integration-test"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision_type"] == "answered"
    assert payload["answer"] == "submitting the previous card is required [E1]."
    assert payload["structured_guidance"]["specific_service"] == chunk[
        "service_name_ar"
    ]
    assert len(payload["citations"]) == 1
    citation = payload["citations"][0]
    assert set(citation) == {
        "doc_code",
        "title",
        "authority",
        "original_url",
        "last_updated",
        "verification_date",
        "version",
        "verification_status",
        "relevance_score",
    }
    assert citation["doc_code"] == chunk["doc_code"]
    assert citation["title"] == chunk["doc_title"]
    assert citation["authority"] == chunk["authority"]
    assert citation["original_url"] == chunk["original_url"]
    assert citation["last_updated"] == chunk["last_updated"]
    assert citation["verification_date"] == chunk["verification_date"]
    assert citation["version"] == chunk["version"]
    assert citation["verification_status"]
    assert citation["relevance_score"] == chunk["rerank_score"]


def test_provider_exception_returns_deterministic_legacy_answer(
    active_rag,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    service, _, _ = active_rag
    private_content_marker = "private-user-content-marker"
    caplog.set_level(logging.WARNING, logger=rag_service_module.__name__)
    set_provider(
        monkeypatch,
        StubLLMProvider(
            error=FakeAPIError(f"API failure for {private_content_marker}")
        ),
    )

    response = service.process_citizen_query(
        ChatRequest(question=QUESTION)
    )

    assert_deterministic_legacy_answer(service, response)
    assert "error_type=FakeAPIError" in caplog.text
    assert private_content_marker not in caplog.text


@pytest.mark.parametrize("invalid_response", ["", "   ", None, {"choices": []}])
def test_empty_or_malformed_provider_output_returns_legacy_answer(
    active_rag,
    monkeypatch: pytest.MonkeyPatch,
    invalid_response: Any,
) -> None:
    service, _, _ = active_rag
    set_provider(monkeypatch, StubLLMProvider(response=invalid_response))

    response = service.process_citizen_query(
        ChatRequest(question=QUESTION)
    )

    assert_deterministic_legacy_answer(service, response)


def test_invalid_generated_citation_returns_deterministic_legacy_answer(
    active_rag,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    service, _, _ = active_rag
    caplog.set_level(logging.WARNING, logger=rag_service_module.__name__)
    set_provider(
        monkeypatch,
        StubLLMProvider(response="Submitting the previous card is required [E99]."),
    )

    response = service.process_citizen_query(
        ChatRequest(question=QUESTION)
    )

    assert_deterministic_legacy_answer(service, response)
    assert "reason=modular_evidence_validation_failed" in caplog.text


def test_failed_generated_answer_grounding_returns_legacy_answer(
    active_rag,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    service, _, _ = active_rag
    caplog.set_level(logging.WARNING, logger=rag_service_module.__name__)
    set_provider(
        monkeypatch,
        StubLLMProvider(
            response="A passport is issued on Mars instead of requiring the previous card [E1]."
        ),
    )

    response = service.process_citizen_query(
        ChatRequest(question=QUESTION)
    )

    assert_deterministic_legacy_answer(service, response)
    assert "reason=legacy_grounding_validation_failed" in caplog.text


def test_insufficient_retrieved_evidence_abstains_without_calling_llm(
    active_rag,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, _, original_evidence_validator = active_rag
    provider_factory_calls: list[bool] = []
    monkeypatch.setattr(
        rag_service_module.evidence_validator,
        "validate_evidence",
        original_evidence_validator,
    )
    monkeypatch.setattr(
        rag_service_module.retrieval_service,
        "retrieve_and_rerank",
        lambda **kwargs: [],
    )
    monkeypatch.setattr(
        rag_service_module,
        "create_llm_provider",
        lambda: provider_factory_calls.append(True),
    )

    response = service.process_citizen_query(
        ChatRequest(question=QUESTION)
    )

    assert response.decision_type == "safe_abstention"
    assert response.status == "abstention"
    assert response.citations == []
    assert provider_factory_calls == []
