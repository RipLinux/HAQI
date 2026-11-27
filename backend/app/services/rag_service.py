
"""
End-to-End RAG Orchestrator & User Journey Service (Slide 7, 10, 16).
Coordinates:
Step 1: User Query
Step 2: Query Understanding
Step 3: Document Retrieval
Step 4: Context Selection & Reranking
Step 5: Evidence Validation & Safe Abstention
Step 6: Grounded Answer Generation
Step 7: Source Citation & Session Logging
"""

import logging
import time
from typing import Optional

from app.database import db_manager
from app.schemas import (
    ChatRequest,
    ChatResponse,
    SourceCitation,
    StructuredGuidance,
)
from app.services.evidence_validator import evidence_validator
from app.services.nlp_integration import nlp_service
from app.services.retrieval_integration import retrieval_service

# Modular RAG imports
from app.contracts.query import UserQuery
from app.modules.retrieval.legacy_adapter import LegacyRetrievalAdapter
from app.modules.rag.context_builder import ContextBuilder
from app.modules.rag.answer_generator import AnswerGenerator
from app.modules.rag.evidence_validator import (
    EvidenceValidator as ModularEvidenceValidator,
)
from app.modules.rag.llm import create_llm_provider

logger = logging.getLogger(__name__)


class RAGOrchestratorService:
    """Orchestrates the RAG pipeline and citizen user journey."""

    def process_citizen_query(self, request: ChatRequest) -> ChatResponse:
        start_total = time.perf_counter()

        # 1. User & Multi-turn Session Resolution
        session = db_manager.get_or_create_session(
            user_id=request.user_id,
            session_id=request.session_id,
        )
        session_id = session["session_id"]

        # Log incoming citizen message
        db_manager.log_chat_message(
            session_id=session_id,
            role="user",
            message_text=request.question,
        )

        # 2. Arabic NLP & Query Understanding
        nlp_result = nlp_service.analyze_query(
            user_query=request.question,
            pending_intent=session.get("pending_intent"),
            awaiting_clarification=session.get("awaiting_clarification", False),
            last_intent=session.get("last_intent"),
            last_sub_type=session.get("last_sub_type"),
        )

        # 3 & 4. Hybrid Retrieval & Reranking
        t_ret_start = time.perf_counter()

        retrieved_chunks = retrieval_service.retrieve_and_rerank(
            nlp_result=nlp_result,
            service_category_filter=request.service_category,
            top_k=3,
        )

        retrieval_time_ms = round(
            (time.perf_counter() - t_ret_start) * 1000.0,
            3,
        )

        # 5. Initial Evidence Validation & Safe Abstention
        validation_report = evidence_validator.validate_evidence(
            nlp_result=nlp_result,
            retrieved_chunks=retrieved_chunks,
        )

        # Handle Path 2a: Clarification Needed
        if validation_report.decision_path == "path_2_clarification":
            db_manager.update_session_clarification(
                session_id=session_id,
                awaiting=True,
                pending_intent=nlp_result.extracted_intent,
                pending_service_slug="national-id",
                options=nlp_result.clarification_options,
            )

            total_latency_ms = round(
                (time.perf_counter() - start_total) * 1000.0,
                3,
            )

            answer_text = (
                nlp_result.clarification_question
                or "يرجى توضيح نوع الإجراء المطلوب."
            )

            db_manager.log_chat_message(
                session_id=session_id,
                role="assistant",
                message_text=answer_text,
                detected_intent=nlp_result.extracted_intent,
                rewritten_query=nlp_result.structured_search_query,
                decision_type="clarification_needed",
                confidence_score=validation_report.max_relevance_score,
                citations=[],
                retrieval_time_ms=retrieval_time_ms,
                total_latency_ms=total_latency_ms,
            )

            return ChatResponse(
                status="success",
                session_id=session_id,
                user_id=request.user_id,
                received_question=request.question,
                decision_type="clarification_needed",
                answer=answer_text,
                structured_guidance=None,
                clarification_question=nlp_result.clarification_question,
                clarification_options=nlp_result.clarification_options,
                sources=[
                    "قطاع الأحوال المدنية - وزارة الداخلية"
                ],
                citations=[],
                nlp_analysis=nlp_result,
                evidence_validation=validation_report,
                metrics={
                    "retrieval_time_ms": retrieval_time_ms,
                    "response_latency_ms": total_latency_ms,
                },
            )

        # Clear pending clarification state
        db_manager.update_session_clarification(
            session_id=session_id,
            awaiting=False,
        )

        # Handle Path 2b: Safe Abstention
        if not validation_report.is_sufficient:
            total_latency_ms = round(
                (time.perf_counter() - start_total) * 1000.0,
                3,
            )

            abstention_msg = (
                validation_report.abstention_reason
                or "امتناع آمن: لا تتوفر وثيقة رسمية موثقة للإجابة على هذا السؤال."
            )

            db_manager.log_chat_message(
                session_id=session_id,
                role="assistant",
                message_text=abstention_msg,
                detected_intent=nlp_result.extracted_intent,
                rewritten_query=nlp_result.structured_search_query,
                decision_type="safe_abstention",
                confidence_score=validation_report.max_relevance_score,
                citations=[],
                retrieval_time_ms=retrieval_time_ms,
                total_latency_ms=total_latency_ms,
            )

            return ChatResponse(
                status="abstention",
                session_id=session_id,
                user_id=request.user_id,
                received_question=request.question,
                decision_type="safe_abstention",
                answer=abstention_msg,
                structured_guidance=None,
                sources=[],
                citations=[],
                nlp_analysis=nlp_result,
                evidence_validation=validation_report,
                metrics={
                    "retrieval_time_ms": retrieval_time_ms,
                    "response_latency_ms": total_latency_ms,
                },
            )

        # Handle Path 1: Verified Context
        primary_chunk = retrieved_chunks[0]

        citation = SourceCitation(
            doc_code=primary_chunk["doc_code"],
            title=primary_chunk["doc_title"],
            authority=primary_chunk["authority"],
            original_url=primary_chunk["original_url"],
            last_updated=primary_chunk["last_updated"],
            verification_date=primary_chunk["verification_date"],
            version=primary_chunk["version"],
            verification_status="موثق رسمياً (Verified Official Source)",
            relevance_score=primary_chunk["rerank_score"],
        )

        ref_summary = (
            f"{primary_chunk['doc_title']} "
            f"({primary_chunk['original_url']}) — "
            f"آخر تحديث: {primary_chunk['last_updated']} | "
            f"تاريخ التحقق: {primary_chunk['verification_date']}"
        )

        structured_guidance = StructuredGuidance(
            specific_service=primary_chunk["service_name_ar"],
            procedural_steps=primary_chunk["steps"],
            required_documents=primary_chunk["required_documents"],
            responsible_authority=primary_chunk["authority"],
            fees_and_duration=(
                f"الرسوم: {primary_chunk['fees_text']} | "
                f"المدة: {primary_chunk['processing_time']}"
            ),
            reference_and_verification=ref_summary,
        )

        # Follow-up questions: return ONLY the requested aspect
        focus = (nlp_result.entities or {}).get("requested_aspect")

        structured_guidance = self._focus_guidance(
            structured_guidance,
            focus,
        )

        # Deterministic fallback answer
        formatted_answer = self._format_arabic_answer(
            structured_guidance,
            focus,
        )

        # 6. Optional Modular LLM Answer Generation
        llm_answer = self._generate_llm_answer(
            question=request.question,
            nlp_result=nlp_result,
            primary_chunk=primary_chunk,
        )

        if llm_answer:
            formatted_answer = llm_answer

        total_latency_ms = round(
            (time.perf_counter() - start_total) * 1000.0,
            3,
        )

        # 7. Source Citation & Session Logging
        db_manager.log_chat_message(
            session_id=session_id,
            role="assistant",
            message_text=formatted_answer,
            detected_intent=nlp_result.extracted_intent,
            rewritten_query=nlp_result.structured_search_query,
            decision_type="answered",
            confidence_score=validation_report.max_relevance_score,
            citations=[citation.model_dump()],
            retrieval_time_ms=retrieval_time_ms,
            total_latency_ms=total_latency_ms,
        )

        # Remember answered service for follow-up questions
        if (
            nlp_result.extracted_intent
            and nlp_result.extracted_intent != "unknown"
        ):
            db_manager.set_session_context(
                session_id=session_id,
                intent=nlp_result.extracted_intent,
                sub_type=nlp_result.sub_type,
            )

        return ChatResponse(
            status="success",
            session_id=session_id,
            user_id=request.user_id,
            received_question=request.question,
            decision_type="answered",
            focus=focus,
            answer=formatted_answer,
            structured_guidance=structured_guidance,
            sources=[
                f"{primary_chunk['authority']} — "
                f"{primary_chunk['doc_title']} "
                f"({primary_chunk['original_url']})"
            ],
            citations=[citation],
            nlp_analysis=nlp_result,
            evidence_validation=validation_report,
            metrics={
                "retrieval_time_ms": retrieval_time_ms,
                "response_latency_ms": total_latency_ms,
            },
        )

    def _generate_llm_answer(
        self,
        question: str,
        nlp_result,
        primary_chunk: dict,
    ) -> Optional[str]:
        """
        Generate an optional answer using the modular RAG pipeline.

        Returns None if the provider is disabled or any generation,
        citation, or legacy grounding validation step fails.
        """

        try:
            # Provider is disabled by default.
            provider = create_llm_provider()

            if provider is None:
                return None

            # Convert the verified legacy retrieval record.
            retrieved = LegacyRetrievalAdapter.convert(
                primary_chunk,
                rank=1,
            )

            # Enrich the evidence with structured service information.
            evidence_parts = [
                retrieved.text or "",
                f"Service: {primary_chunk.get('service_name_ar', '')}",
                f"Authority: {primary_chunk.get('authority', '')}",
                f"Steps: {primary_chunk.get('steps', [])}",
                (
                    "Required documents: "
                    f"{primary_chunk.get('required_documents', [])}"
                ),
                f"Fees: {primary_chunk.get('fees_text', '')}",
                (
                    "Processing time: "
                    f"{primary_chunk.get('processing_time', '')}"
                ),
            ]

            retrieved = retrieved.model_copy(
                update={
                    "text": "\n".join(evidence_parts),
                }
            )

            # Only one chunk is passed because the current API returns
            # one primary citation.
            context = ContextBuilder(
                max_chunks=1,
            ).build([retrieved])

            query = UserQuery(
                text=question,
                language="ar",
            )

            # Generate the answer.
            answer_text = AnswerGenerator(
                provider=provider,
            ).generate(
                query=query,
                context=context,
            )

            # Validate evidence identifiers such as [E1].
            modular_validation = ModularEvidenceValidator().validate(
                answer_text=answer_text,
                context=context,
            )

            if (
                not modular_validation.valid
                or modular_validation.answer.abstained
            ):
                logger.warning(
                    "Optional LLM answer rejected; using deterministic legacy fallback "
                    "(reason=modular_evidence_validation_failed)"
                )
                return None

            # Check generated-answer grounding only.
            # Initial source, relevance, freshness, and contradiction
            # validation has already succeeded in the main RAG flow.
            is_grounded = evidence_validator.validate_generated_answer(
                top_chunk=primary_chunk,
                proposed_answer=modular_validation.answer.text,
            )

            if not is_grounded:
                logger.warning(
                    "Optional LLM answer rejected; using deterministic legacy fallback "
                    "(reason=legacy_grounding_validation_failed)"
                )
                return None

            return modular_validation.answer.text

        except Exception as exc:
            # The LLM is optional. Any failure must preserve the
            # deterministic answer and must not break the API request.
            # Omit exception text and traceback to avoid logging prompts,
            # provider response data, or credentials.
            logger.warning(
                "Optional LLM generation failed; using deterministic legacy fallback "
                "(error_type=%s)",
                type(exc).__name__,
            )
            return None

    _FOCUS_TITLES = {
        "documents": "قائمة المستندات المطلوبة",
        "steps": "الخطوات الإجرائية",
        "fees_duration": "الرسوم والمدة الزمنية",
        "authority": "الجهة المسؤولة",
    }

    def _focus_guidance(
        self,
        guidance: StructuredGuidance,
        focus: Optional[str],
    ) -> StructuredGuidance:
        """Blank sections the citizen did not ask about."""

        if focus not in self._FOCUS_TITLES:
            return guidance

        data = guidance.model_dump()

        if focus != "steps":
            data["procedural_steps"] = []

        if focus != "documents":
            data["required_documents"] = []

        if focus != "fees_duration":
            data["fees_and_duration"] = ""

        return StructuredGuidance(**data)

    def _format_arabic_answer(
        self,
        guidance: StructuredGuidance,
        focus: Optional[str] = None,
    ) -> str:

        if focus in self._FOCUS_TITLES:
            if focus == "steps":
                body = "\n".join(
                    f"  {i + 1}. {step}"
                    for i, step in enumerate(guidance.procedural_steps)
                )

            elif focus == "documents":
                body = "\n".join(
                    f"  - {document}"
                    for document in guidance.required_documents
                )

            elif focus == "fees_duration":
                body = f"  {guidance.fees_and_duration}"

            else:
                body = f"  {guidance.responsible_authority}"

            return (
                f"• الخدمة المحددة: {guidance.specific_service}\n"
                f"• {self._FOCUS_TITLES[focus]}:\n"
                f"{body}\n"
                f"• المرجع وحالة التحقق: "
                f"{guidance.reference_and_verification}\n"
                f"* {guidance.methodological_note}"
            )

        steps_str = "\n".join(
            f"  {i + 1}. {step}"
            for i, step in enumerate(guidance.procedural_steps)
        )

        docs_str = "\n".join(
            f"  - {document}"
            for document in guidance.required_documents
        )

        return (
            f"• الخدمة المحددة: {guidance.specific_service}\n"
            f"• الخطوات الإجرائية:\n{steps_str}\n"
            f"• قائمة المستندات المطلوبة:\n{docs_str}\n"
            f"• الجهة المسؤولة: {guidance.responsible_authority}\n"
            f"• الرسوم والمدة الزمنية: {guidance.fees_and_duration}\n"
            f"• المرجع وحالة التحقق: "
            f"{guidance.reference_and_verification}\n"
            f"* {guidance.methodological_note}"
        )


rag_service = RAGOrchestratorService()
