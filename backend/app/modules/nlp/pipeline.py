"""Main Arabic NLP pipeline orchestrating query processing."""

from app.contracts.nlp import NlpOutput
from app.contracts.query import UserQuery

from .clarification import check_clarification_needed
from .dialect import convert_dialect_to_msa
from .extractor import classify_intent, extract_entities
from .normalizer import normalize_arabic_text
from .rewriter import rewrite_query


def process_user_query(query: UserQuery) -> NlpOutput:
    """Process an incoming Arabic UserQuery and produce a structured NlpOutput."""
    normalized = normalize_arabic_text(query.text)
    msa_text = convert_dialect_to_msa(normalized)

    intent, confidence = classify_intent(msa_text)
    entities = extract_entities(msa_text)

    needs_clarification, clarification_question = check_clarification_needed(
        intent=intent,
        entities=entities,
        normalized_text=normalized,
    )

    if needs_clarification:
        return NlpOutput(
            intent=intent,
            entities=entities,
            normalized_query=normalized,
            rewritten_query=None,
            retrieval_query=None,
            clarification_needed=True,
            clarification_question=clarification_question,
            confidence=confidence,
        )

    rewritten = rewrite_query(intent=intent, entities=entities, msa_text=msa_text)
    retrieval_query = rewritten or msa_text or normalized

    return NlpOutput(
        intent=intent,
        entities=entities,
        normalized_query=normalized,
        rewritten_query=rewritten,
        retrieval_query=retrieval_query,
        clarification_needed=False,
        clarification_question=None,
        confidence=confidence,
    )
