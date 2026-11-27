
"""Validate evidence references and build trusted answer citations."""

import re
from dataclasses import dataclass

from app.contracts.answers import Answer, Citation
from app.modules.rag.context_builder import ContextBuildResult


EVIDENCE_PATTERN = re.compile(r"\[E(\d+)\]")


@dataclass(frozen=True, slots=True)
class EvidenceValidationResult:
    """Result of validating an LLM-generated answer."""

    answer: Answer
    valid: bool
    invalid_evidence_ids: tuple[str, ...] = ()


class EvidenceValidator:
    """Validate evidence IDs against the exact context sent to the LLM."""

    def validate(
        self,
        answer_text: str,
        context: ContextBuildResult,
    ) -> EvidenceValidationResult:
        """Validate references and construct citations from trusted chunks."""

        if not answer_text or not answer_text.strip():
            return self._abstain("The generated answer is empty.")

        # Reject malformed evidence references instead of silently ignoring them.
        evidence_tokens = re.findall(r"\[E[^\]]*\]", answer_text)

        malformed_references = [
            token
            for token in evidence_tokens
            if not EVIDENCE_PATTERN.fullmatch(token)
        ]

        if malformed_references:
            return self._abstain(
                "The answer contains malformed evidence references.",
                invalid_ids=tuple(
                    token[1:-1] for token in malformed_references
                ),
            )

        evidence_ids = EVIDENCE_PATTERN.findall(answer_text)

        if not evidence_ids:
            return self._abstain(
                "The answer contains no verifiable evidence references."
            )

        unique_ids = list(dict.fromkeys(evidence_ids))

        if not context.chunks:
            return self._abstain("No evidence is available.")

        if len(unique_ids) > len(context.chunks):
            return self._abstain(
                "The answer contains references that cannot be verified."
            )

        citations: list[Citation] = []

        for evidence_id in unique_ids:
            index = int(evidence_id) - 1

            if index < 0 or index >= len(context.chunks):
                return self._abstain(
                    "The answer contains references that cannot be verified.",
                    invalid_ids=(f"E{evidence_id}",),
                )

            chunk = context.chunks[index]

            citations.append(
                Citation(
                    chunk_id=chunk.chunk_id,
                    source_url=chunk.source_url,
                    label=f"E{evidence_id}",
                )
            )

        return EvidenceValidationResult(
            answer=Answer(
                text=answer_text.strip(),
                citations=citations,
                abstained=False,
            ),
            valid=True,
        )

    @staticmethod
    def _abstain(
        reason: str,
        invalid_ids: tuple[str, ...] = (),
    ) -> EvidenceValidationResult:
        return EvidenceValidationResult(
            answer=Answer(
                text="I cannot provide a reliable answer based on the available evidence.",
                citations=[],
                abstained=True,
                abstention_reason=reason,
            ),
            valid=False,
            invalid_evidence_ids=invalid_ids,
        )
