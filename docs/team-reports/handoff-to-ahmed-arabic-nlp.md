# Handoff to Ahmed Rabie: Arabic NLP (CONFIRMED)

## Confirmed Contract & Retrieval Boundary

- **Input Contract:** `UserQuery` (`text`, `language`, `conversation_id`) in `backend/app/contracts/query.py`.
- **Output Contract:** `NlpOutput` in `backend/app/contracts/nlp.py`.
- **Canonical Field for Retrieval:** `NlpOutput.retrieval_query` is the single canonical query string to be passed directly into `RetrievalRequest.query`.

## Confirmed Processing Behavior

1. **Normalization & Spelling (`normalizer.py`):** Strips diacritics, tatweel, character elongation, and punctuation noise while correcting common Arabic spelling variations (Teh Marbuta and Hamzas) consistent with ingestion cleaning.
2. **Egyptian Dialect & Query Rewriting (`dialect.py`, `rewriter.py`):** Converts Egyptian colloquial phrases and service terms into formal MSA search queries and aligns with the synthetic evaluation queries.
3. **Intent & Entities (`extractor.py`):** Populates `intent`, `confidence`, and `entities` (`government_service`, `action_type`, `government_agency`).
4. **Clarification Handling (`clarification.py`):** When a query lacks a target service or agency, `clarification_needed` is set to `True`, `clarification_question` provides a prompt for the user, and `retrieval_query` is set to `None`. Retrieval must not be called when `clarification_needed` is `True`.