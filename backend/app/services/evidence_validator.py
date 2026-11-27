"""
Evidence Validation & Safe Abstention Engine (Slide 12, 19, 22).
Developed by Maha in collaboration with Hassan (RAG Lead):
- هوية المصدر (Source Identity): التحقق من تبعية الوثيقة لجهة رسمية معتمدة.
- فحص الصلة (Relevance Check): مطابقة الدليل المسترجع مع سؤال المواطن.
- تتبع التواريخ (Date Tracking): رصد تاريخ النشر وآخر تحديث متاح.
- كشف التعارض (Contradiction Detection): رصد التناقضات وتحويلها للمراجعة البشرية.
- المسار 1: توفر أدلة كافية (Sufficient Evidence) -> سياق موثق (Verified Context) -> إجابة مدعومة بالمصادر والروابط.
- المسار 2: عدم كفاية الأدلة (Insufficient Evidence) -> منع التخمين التوليدي -> طلب توضيح أو امتناع آمن (Safe Abstention).
"""

from datetime import datetime
import re
from typing import Any
from urllib.parse import urlparse

from app.config import settings
from app.database import db_manager
from app.schemas import EvidenceValidationReport, NLPAnalysisResult
from app.services.nlp_integration import normalize_arabic_text


class EvidenceValidationService:
    """Implements the 4-pillar Evidence Validation & Safe Abstention mechanism (Slide 12)."""

    def validate_evidence(
        self,
        nlp_result: NLPAnalysisResult,
        retrieved_chunks: list[dict[str, Any]],
        proposed_answer: str | None = None,
    ) -> EvidenceValidationReport:
        # 1. Guardrail: Legal Fatwa / Litigation Strategy Request -> Immediate Safe Abstention (Slide 19)
        if nlp_result.is_legal_opinion_request:
            return EvidenceValidationReport(
                is_sufficient=False,
                decision_path="path_2_safe_abstention",
                source_identity_verified=False,
                relevance_passed=False,
                max_relevance_score=0.0,
                grounding_score=0.0,
                freshness_status="not_applicable",
                contradiction_detected=False,
                abstention_reason=(
                    "امتناع آمن (Safe Abstention): نظام «حقي» يقدم إرشاداً إجرائياً مبنياً على اللوائح الحكومية الرسمية فقط، "
                    "ولا يقدم فتاوى قانونية أو استشارات قضائية في النزاعات. يُرجى استشارة محامٍ مختص أو التوجه للمساعدة القضائية."
                ),
            )

        # 2. Path 2a: Ambiguous procedural query -> Request Clarification instead of guessing (Slide 7, 12, 16)
        if nlp_result.needs_clarification:
            return EvidenceValidationReport(
                is_sufficient=False,
                decision_path="path_2_clarification",
                source_identity_verified=True,
                relevance_passed=True,
                max_relevance_score=0.75,
                grounding_score=1.0,
                freshness_status="verified_up_to_date",
                contradiction_detected=False,
                abstention_reason=(
                    "طلب توضيح لمنع التخمين التوليدي: السؤال يحتمل أكثر من إجراء فرعي مختلف في المستندات والخطوات."
                ),
            )

        # 3. Check if out-of-scope or no retrieved chunks
        if nlp_result.is_out_of_scope or not retrieved_chunks:
            return EvidenceValidationReport(
                is_sufficient=False,
                decision_path="path_2_safe_abstention",
                source_identity_verified=False,
                relevance_passed=False,
                max_relevance_score=retrieved_chunks[0]["rerank_score"] if retrieved_chunks else 0.0,
                grounding_score=0.0,
                freshness_status="no_verified_source",
                contradiction_detected=False,
                abstention_reason=(
                    "امتناع آمن (Safe Abstention): لا يتوفر دليل رسمي موثق في قاعدة المعرفة الحكومية يجيب على هذا الاستفسار بدقة. "
                    "يمتنع النظام عن التوليد التخميني حفاظاً على موثوقية المعلومة."
                ),
            )

        top_chunk = retrieved_chunks[0]
        max_rel_score = float(top_chunk.get("rerank_score", 0.0))

        # Pillar 1: هوية المصدر (Source Identity Verification)
        source_verified = self._verify_source_authority(top_chunk)

        # Pillar 2: فحص الصلة (Relevance Check against threshold)
        relevance_passed = max_rel_score >= settings.min_relevance_score

        # Pillar 3: تتبع التواريخ (Date & Freshness Tracking)
        freshness_status = self._check_source_freshness(top_chunk)

        # Pillar 4: كشف التعارض (Contradiction Detection across chunks of same service/subtype)
        contradiction_detected, contradiction_details = self._detect_contradictions(
            nlp_result.original_text, retrieved_chunks
        )

        # Grounding Score calculation (verifies proposed answer or chunk completeness)
        grounding_score = self._compute_grounding_score(top_chunk, proposed_answer)

        # If Contradiction is detected -> Safe Abstention & Route to Human Review (Slide 12, 19, 22)
        if contradiction_detected:
            return EvidenceValidationReport(
                is_sufficient=False,
                decision_path="path_2_safe_abstention",
                source_identity_verified=source_verified,
                relevance_passed=relevance_passed,
                max_relevance_score=max_rel_score,
                grounding_score=grounding_score,
                freshness_status=freshness_status,
                contradiction_detected=True,
                contradiction_details=contradiction_details,
                abstention_reason=(
                    "امتناع آمن بسبب تعارض المصادر (Conflicting Sources): تم رصد تعارض بين وثيقتين وإحالة الموضوع للمراجعة البشرية."
                ),
            )

        # If Source is not official, Relevance is too low, or Source is expired -> Safe Abstention
        if (
            not source_verified
            or not relevance_passed
            or freshness_status == "outdated_unverified"
            or grounding_score < settings.min_grounding_score
        ):
            reason = "امتناع آمن (Safe Abstention): الأدلة المسترجعة غير كافية أو غير معتمدة رسمياً."
            if not source_verified:
                reason = "امتناع آمن: الوثيقة المسترجعة لا تنتمي لجهة حكومية رسمية معتمدة."
            elif freshness_status == "outdated_unverified":
                reason = "امتناع آمن: الوثيقة المسترجعة قديمة وتجاوزت فترة التحقق المسموحة."
            elif grounding_score < settings.min_grounding_score:
                reason = "امتناع آمن: الإجابة المقترحة تتضمن ادعاءات غير مسندة للدليل الرسمي."

            return EvidenceValidationReport(
                is_sufficient=False,
                decision_path="path_2_safe_abstention",
                source_identity_verified=source_verified,
                relevance_passed=relevance_passed,
                max_relevance_score=max_rel_score,
                grounding_score=grounding_score,
                freshness_status=freshness_status,
                contradiction_detected=False,
                abstention_reason=reason,
            )

        # Path 1: Sufficient Evidence -> Verified Context
        return EvidenceValidationReport(
            is_sufficient=True,
            decision_path="path_1_verified_context",
            source_identity_verified=True,
            relevance_passed=True,
            max_relevance_score=max_rel_score,
            grounding_score=grounding_score,
            freshness_status=freshness_status,
            contradiction_detected=False,
            abstention_reason=None,
        )

    def _verify_source_authority(self, chunk: dict[str, Any]) -> bool:
        if not chunk.get("is_official_verified", False):
            return False
        authority = chunk.get("authority", "")
        url = chunk.get("original_url", "")
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        domain_ok = any( domain == td or domain.endswith("." + td) for td in settings.trusted_domains )
        auth_ok = any(ta in authority for ta in settings.trusted_authorities)
        return domain_ok and auth_ok

    def _check_source_freshness(self, chunk: dict[str, Any]) -> str:
        last_updated_str = chunk.get("last_updated", "2025-01-01")
        try:
            updated_dt = datetime.strptime(last_updated_str, "%Y-%m-%d")
            age_days = (datetime.utcnow() - updated_dt).days
            if age_days > settings.max_doc_age_days:
                return "outdated_unverified"
            return "verified_up_to_date"
        except ValueError:
            return "verified_up_to_date"

    def _detect_contradictions(
        self, query_text: str, chunks: list[dict[str, Any]]
    ) -> tuple[bool, str | None]:
        """Detects if two high-scoring chunks for the exact same intent & subtype contradict on fees or steps."""
        if len(chunks) < 2:
            return False, None
        first, second = chunks[0], chunks[1]
        if (
            first.get("intent_tag") == second.get("intent_tag")
            and first.get("sub_type") == second.get("sub_type")
            and first.get("doc_code") != second.get("doc_code")
            and second.get("rerank_score", 0.0) >= settings.min_relevance_score
        ):
            if first.get("fees_text") != second.get("fees_text") or first.get("steps") != second.get("steps"):
                desc = (
                    f"تعارض مرصود في إجراءات/رسوم ({first.get('service_name_ar')}) "
                    f"بين الوثيقة {first.get('doc_code')} والوثيقة {second.get('doc_code')}."
                )
                db_manager.create_contradiction_flag(
                    query_text=query_text,
                    doc_code_a=first.get("doc_code", "DOC-A"),
                    doc_code_b=second.get("doc_code", "DOC-B"),
                    conflict_description=desc,
                )
                return True, desc
        return False, None

    @staticmethod
    def _normalize_numeric_digits(text: str) -> str:
        digit_map = str.maketrans(
            "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"
            "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9",
            "01234567890123456789",
        )
        return text.translate(digit_map)

    def _has_unsupported_numeric_claim(
        self,
        top_chunk: dict[str, Any],
        proposed_answer: str,
    ) -> bool:
        """Reject numeric claims not supported by their corresponding source field."""
        answer = self._normalize_numeric_digits(proposed_answer)

        claim_patterns = [
            (
                re.compile(
                    r"(?:\u0627\u0644\u0631\u0633\u0648\u0645|\u0631\u0633\u0648\u0645|"
                    r"\u0627\u0644\u062a\u0643\u0644\u0641\u0629|\u0627\u0644\u0645\u0628\u0644\u063a|"
                    r"\u0642\u064a\u0645\u0629\s+\u0627\u0644\u0631\u0633\u0648\u0645)"
                ),
                "fees_text",
            ),
            (
                re.compile(
                    r"(?:\u0645\u062f\u0629\s+\u0627\u0644\u0625\u062c\u0631\u0627\u0621|"
                    r"\u0627\u0644\u0645\u062f\u0629|\u0645\u062f\u0629|"
                    r"\u0648\u0642\u062a\s+\u0627\u0644\u062a\u0646\u0641\u064a\u0630|"
                    r"\u0641\u062a\u0631\u0629\s+\u0627\u0644\u062a\u0646\u0641\u064a\u0630)"
                ),
                "processing_time",
            ),
        ]

        claims = []
        for pattern, field in claim_patterns:
            for match in pattern.finditer(answer):
                claims.append((match.start(), match.end(), field))

        claims.sort(key=lambda item: item[0])

        for index, (_, start, field) in enumerate(claims):
            end = claims[index + 1][0] if index + 1 < len(claims) else len(answer)
            segment = answer[start:end]

            # Stop at punctuation separating clauses or sentences.
            segment = re.split(r"[\u060c,\u061b;.!?\u061f\n]", segment, maxsplit=1)[0]

            answer_numbers = re.findall(r"\d+(?:[.,]\d+)?", segment)
            if not answer_numbers:
                continue

            source_text = self._normalize_numeric_digits(
                str(top_chunk.get(field) or "")
            )
            source_numbers = set(
                re.findall(r"\d+(?:[.,]\d+)?", source_text)
            )

            if any(number not in source_numbers for number in answer_numbers):
                return True

        return False

    def validate_generated_answer(
        self,
        top_chunk: dict[str, Any],
        proposed_answer: str,
    ) -> bool:
        """Validate generated-answer grounding without rerunning safety checks."""
        if self._has_unsupported_numeric_claim(top_chunk, proposed_answer):
            return False

        score = self._compute_generated_answer_grounding_score(
            top_chunk,
            proposed_answer,
        )
        return score >= settings.min_grounding_score

    def _compute_generated_answer_grounding_score(
        self,
        top_chunk: dict[str, Any],
        proposed_answer: str,
    ) -> float:
        """Compare generated-answer tokens against all available chunk evidence."""
        if not proposed_answer or not proposed_answer.strip():
            return 0.0

        evidence_parts = [
            str(top_chunk.get("service_name_ar") or ""),
            str(top_chunk.get("chunk_text") or ""),
            str(top_chunk.get("authority") or ""),
            str(top_chunk.get("fees_text") or ""),
            str(top_chunk.get("processing_time") or ""),
        ]

        for field in ("steps", "required_documents"):
            value = top_chunk.get(field) or []
            if isinstance(value, (list, tuple, set)):
                evidence_parts.extend(str(item) for item in value)
            else:
                evidence_parts.append(str(value))

        evidence_tokens = set(
            normalize_arabic_text(" ".join(evidence_parts)).split()
        )

        answer_tokens = [
            token
            for token in normalize_arabic_text(proposed_answer).split()
            if (len(token) > 2 or token.isdigit())
            and not (
                token.lower().startswith("e")
                and token[1:].isdigit()
            )
        ]

        if not answer_tokens:
            return 0.0

        overlap = sum(
            1 for token in answer_tokens if token in evidence_tokens
        )
        return round(overlap / len(answer_tokens), 4)

    def _compute_grounding_score(
        self, top_chunk: dict[str, Any], proposed_answer: str | None = None
    ) -> float:
        if not proposed_answer:
            # Grounded generation directly from verified chunk structure has 1.0 faithfulness
            return 1.0 if top_chunk.get("steps") and top_chunk.get("required_documents") else 0.75

        evidence_text = " ".join(
            [
                top_chunk.get("service_name_ar", ""),
                top_chunk.get("chunk_text", ""),
                top_chunk.get("authority", ""),
                " ".join(top_chunk.get("steps", [])),
                " ".join(top_chunk.get("required_documents", [])),
            ]
        )
        ev_tokens = set(normalize_arabic_text(evidence_text).split())
        ans_tokens = [
            t
            for t in normalize_arabic_text(proposed_answer).split()
            if len(t) > 2
        ]
        if not ans_tokens:
            return 0.0
        overlap = sum(1 for t in ans_tokens if t in ev_tokens)
        return round(min(1.0, overlap / max(len(ans_tokens), 1)), 4)


evidence_validator = EvidenceValidationService()
