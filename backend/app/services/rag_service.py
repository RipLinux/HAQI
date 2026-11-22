"""
End-to-End RAG Orchestrator & User Journey Service (Slide 7, 10, 16).
Coordinates:
Step 1: User Query (Ø¥Ø¯Ø®Ø§Ù„ Ø§Ù„Ø³Ø¤Ø§Ù„ Ø¨Ø§Ù„Ø¹Ø±Ø¨ÙŠØ©)
Step 2: Query Understanding (ÙÙ‡Ù… Ø§Ù„Ù‚ØµØ¯ ÙˆØªØ­Ø¯ÙŠØ¯ Ø§Ù„Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø§Ù„Ù†Ø§Ù‚ØµØ© - Ahmed Rabie's module)
Step 3: Document Retrieval (Ø§Ù„Ø¨Ø­Ø« Ø§Ù„Ù‡Ø¬ÙŠÙ† ÙÙŠ Ø§Ù„Ù…ØµØ§Ø¯Ø± Ø§Ù„Ø±Ø³Ù…ÙŠØ© - Anas's module)
Step 4: Context Selection & Reranking (ØªØ±ØªÙŠØ¨ ÙˆØªØ¯Ù‚ÙŠÙ‚ Ø§Ù„Ø£Ø¯Ù„Ø©)
Step 5: Evidence Validation & Safe Abstention (Ø§Ù„ØªØ­Ù‚Ù‚ ÙˆØ§Ù„Ø§Ù…ØªÙ†Ø§Ø¹ Ø§Ù„Ø¢Ù…Ù† - Maha & Hassan)
Step 6: Grounded Answer Generation (ØªÙˆÙ„ÙŠØ¯ Ø¥Ø¬Ø§Ø¨Ø© Ù…Ù‡ÙŠÙƒÙ„Ø© Ù…Ø¨Ø³Ø·Ø©)
Step 7: Source Citation & Session Logging (Ø¥Ø±ÙØ§Ù‚ Ø§Ù„Ù…ØµØ§Ø¯Ø± ÙˆØ§Ù„Ø®Ø·ÙˆØ§Øª ÙˆØ­ÙØ¸ Ø§Ù„Ø¬Ù„Ø³Ø©)
"""

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


class RAGOrchestratorService:
    """Orchestrates the 7-stage RAG pipeline and 9-step citizen user journey."""

    def process_citizen_query(self, request: ChatRequest) -> ChatResponse:
        start_total = time.perf_counter()

        # 1. User & Multi-turn Session Resolution
        session = db_manager.get_or_create_session(
            user_id=request.user_id, session_id=request.session_id
        )
        session_id = session["session_id"]

        # Log incoming citizen message
        db_manager.log_chat_message(
            session_id=session_id,
            role="user",
            message_text=request.question,
        )

        # 2. Arabic NLP & Query Understanding (Slide 9)
        nlp_result = nlp_service.analyze_query(
            user_query=request.question,
            pending_intent=session.get("pending_intent"),
            awaiting_clarification=session.get("awaiting_clarification", False),
            last_intent=session.get("last_intent"),
            last_sub_type=session.get("last_sub_type"),
        )

        # 3 & 4. Hybrid Retrieval & Cross-Encoder Reranking (Slide 11)
        t_ret_start = time.perf_counter()
        retrieved_chunks = retrieval_service.retrieve_and_rerank(
            nlp_result=nlp_result,
            service_category_filter=request.service_category,
            top_k=3,
        )
        retrieval_time_ms = round((time.perf_counter() - t_ret_start) * 1000.0, 3)

        # 5. Evidence Validation & Safe Abstention (Slide 12)
        validation_report = evidence_validator.validate_evidence(
            nlp_result=nlp_result,
            retrieved_chunks=retrieved_chunks,
        )

        # Handle Path 2a: Clarification Needed (Slide 7 Step 4 & Slide 16)
        if validation_report.decision_path == "path_2_clarification":
            db_manager.update_session_clarification(
                session_id=session_id,
                awaiting=True,
                pending_intent=nlp_result.extracted_intent,
                pending_service_slug="national-id",
                options=nlp_result.clarification_options,
            )
            total_latency_ms = round((time.perf_counter() - start_total) * 1000.0, 3)
            answer_text = nlp_result.clarification_question or "ÙŠØ±Ø¬Ù‰ ØªÙˆØ¶ÙŠØ­ Ù†ÙˆØ¹ Ø§Ù„Ø¥Ø¬Ø±Ø§Ø¡ Ø§Ù„Ù…Ø·Ù„ÙˆØ¨."

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
                sources=["Ù‚Ø·Ø§Ø¹ Ø§Ù„Ø£Ø­ÙˆØ§Ù„ Ø§Ù„Ù…Ø¯Ù†ÙŠØ© - ÙˆØ²Ø§Ø±Ø© Ø§Ù„Ø¯Ø§Ø®Ù„ÙŠØ©"],
                citations=[],
                nlp_analysis=nlp_result,
                evidence_validation=validation_report,
                metrics={
                    "retrieval_time_ms": retrieval_time_ms,
                    "response_latency_ms": total_latency_ms,
                },
            )

        # Clear any pending clarification state once resolved or abstained
        db_manager.update_session_clarification(session_id=session_id, awaiting=False)

        # Handle Path 2b: Safe Abstention (Slide 12 & 19)
        if not validation_report.is_sufficient:
            total_latency_ms = round((time.perf_counter() - start_total) * 1000.0, 3)
            abstention_msg = (
                validation_report.abstention_reason
                or "Ø§Ù…ØªÙ†Ø§Ø¹ Ø¢Ù…Ù†: Ù„Ø§ ØªØªÙˆÙØ± ÙˆØ«ÙŠÙ‚Ø© Ø±Ø³Ù…ÙŠØ© Ù…ÙˆØ«Ù‚Ø© Ù„Ù„Ø¥Ø¬Ø§Ø¨Ø© Ø¹Ù„Ù‰ Ù‡Ø°Ø§ Ø§Ù„Ø³Ø¤Ø§Ù„."
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

        # Handle Path 1: Verified Context -> Structured Grounded Answer (Slide 16)
        primary_chunk = retrieved_chunks[0]
        citation = SourceCitation(
            doc_code=primary_chunk["doc_code"],
            title=primary_chunk["doc_title"],
            authority=primary_chunk["authority"],
            original_url=primary_chunk["original_url"],
            last_updated=primary_chunk["last_updated"],
            verification_date=primary_chunk["verification_date"],
            version=primary_chunk["version"],
            verification_status="Ù…ÙˆØ«Ù‚ Ø±Ø³Ù…ÙŠØ§Ù‹ (Verified Official Source)",
            relevance_score=primary_chunk["rerank_score"],
        )

        ref_summary = (
            f"{primary_chunk['doc_title']} ({primary_chunk['original_url']}) â€” "
            f"Ø¢Ø®Ø± ØªØ­Ø¯ÙŠØ«: {primary_chunk['last_updated']} | ØªØ§Ø±ÙŠØ® Ø§Ù„ØªØ­Ù‚Ù‚: {primary_chunk['verification_date']}"
        )

        structured_guidance = StructuredGuidance(
            specific_service=primary_chunk["service_name_ar"],
            procedural_steps=primary_chunk["steps"],
            required_documents=primary_chunk["required_documents"],
            responsible_authority=primary_chunk["authority"],
            fees_and_duration=f"Ø§Ù„Ø±Ø³ÙˆÙ…: {primary_chunk['fees_text']} | Ø§Ù„Ù…Ø¯Ø©: {primary_chunk['processing_time']}",
            reference_and_verification=ref_summary,
        )

        # Follow-up questions: return ONLY the part the citizen asked about
        focus = (nlp_result.entities or {}).get("requested_aspect")
        structured_guidance = self._focus_guidance(structured_guidance, focus)
        formatted_answer = self._format_arabic_answer(structured_guidance, focus)
        total_latency_ms = round((time.perf_counter() - start_total) * 1000.0, 3)

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

        # Remember the answered service so the next follow-up question has context
        if nlp_result.extracted_intent and nlp_result.extracted_intent != "unknown":
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
                f"{primary_chunk['authority']} â€” {primary_chunk['doc_title']} ({primary_chunk['original_url']})"
            ],
            citations=[citation],
            nlp_analysis=nlp_result,
            evidence_validation=validation_report,
            metrics={
                "retrieval_time_ms": retrieval_time_ms,
                "response_latency_ms": total_latency_ms,
            },
        )

    _FOCUS_TITLES = {
        "documents": "Ù‚Ø§Ø¦Ù…Ø© Ø§Ù„Ù…Ø³ØªÙ†Ø¯Ø§Øª Ø§Ù„Ù…Ø·Ù„ÙˆØ¨Ø©",
        "steps": "Ø§Ù„Ø®Ø·ÙˆØ§Øª Ø§Ù„Ø¥Ø¬Ø±Ø§Ø¦ÙŠØ©",
        "fees_duration": "Ø§Ù„Ø±Ø³ÙˆÙ… ÙˆØ§Ù„Ù…Ø¯Ø© Ø§Ù„Ø²Ù…Ù†ÙŠØ©",
        "authority": "Ø§Ù„Ø¬Ù‡Ø© Ø§Ù„Ù…Ø³Ø¤ÙˆÙ„Ø©",
    }

    def _focus_guidance(
        self, guidance: StructuredGuidance, focus: Optional[str]
    ) -> StructuredGuidance:
        """Blank the sections the citizen did not ask about (keeps service, authority, reference)."""
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
        self, guidance: StructuredGuidance, focus: Optional[str] = None
    ) -> str:
        if focus in self._FOCUS_TITLES:
            if focus == "steps":
                body = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(guidance.procedural_steps))
            elif focus == "documents":
                body = "\n".join(f"  - {d}" for d in guidance.required_documents)
            elif focus == "fees_duration":
                body = f"  {guidance.fees_and_duration}"
            else:
                body = f"  {guidance.responsible_authority}"
            return (
                f"â€¢ Ø§Ù„Ø®Ø¯Ù…Ø© Ø§Ù„Ù…Ø­Ø¯Ø¯Ø©: {guidance.specific_service}\n"
                f"â€¢ {self._FOCUS_TITLES[focus]}:\n{body}\n"
                f"â€¢ Ø§Ù„Ù…Ø±Ø¬Ø¹ ÙˆØ­Ø§Ù„Ø© Ø§Ù„ØªØ­Ù‚Ù‚: {guidance.reference_and_verification}\n"
                f"* {guidance.methodological_note}"
            )
        steps_str = "\n".join(
            f"  {i+1}. {s}" for i, s in enumerate(guidance.procedural_steps)
        )
        docs_str = "\n".join(f"  - {d}" for d in guidance.required_documents)
        return (
            f"â€¢ Ø§Ù„Ø®Ø¯Ù…Ø© Ø§Ù„Ù…Ø­Ø¯Ø¯Ø©: {guidance.specific_service}\n"
            f"â€¢ Ø§Ù„Ø®Ø·ÙˆØ§Øª Ø§Ù„Ø¥Ø¬Ø±Ø§Ø¦ÙŠØ©:\n{steps_str}\n"
            f"â€¢ Ù‚Ø§Ø¦Ù…Ø© Ø§Ù„Ù…Ø³ØªÙ†Ø¯Ø§Øª Ø§Ù„Ù…Ø·Ù„ÙˆØ¨Ø©:\n{docs_str}\n"
            f"â€¢ Ø§Ù„Ø¬Ù‡Ø© Ø§Ù„Ù…Ø³Ø¤ÙˆÙ„Ø©: {guidance.responsible_authority}\n"
            f"â€¢ Ø§Ù„Ø±Ø³ÙˆÙ… ÙˆØ§Ù„Ù…Ø¯Ø© Ø§Ù„Ø²Ù…Ù†ÙŠØ©: {guidance.fees_and_duration}\n"
            f"â€¢ Ø§Ù„Ù…Ø±Ø¬Ø¹ ÙˆØ­Ø§Ù„Ø© Ø§Ù„ØªØ­Ù‚Ù‚: {guidance.reference_and_verification}\n"
            f"* {guidance.methodological_note}"
        )


rag_service = RAGOrchestratorService()
