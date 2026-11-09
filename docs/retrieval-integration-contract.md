# Retrieval integration contract

This document records provisional handoffs pending confirmation by each owner.

- **Mohamed:** provide canonical Chunk and Document IDs, text, source URL, and
  citation metadata. Retrieval requires a stable chunk ID and an embedding
  column whose dimension matches the selected model.
- **Ahmed:** provide the processed query, preferably `normalized_query` or
  `rewritten_query`. Retrieval does not normalize Arabic or classify intent.
- **Maha:** confirm the async session, table/column mapping, migration, and
  transaction conventions. `PgVectorStore` accepts an existing session and does
  not define ORM models.
- **Hassan:** consume `RankedRetrievalResults`; scores are comparable only
  within a method. RRF scores are fusion scores, not vector similarities.
- **Heba:** use `http://backend:8000/api/v1` from a container and
  `http://localhost:8000/api/v1` from the host.

No government documents, real judgments, production embedding dimension, or
embedding model have been selected by this module.
## Retrieval hardening interface

`RetrievalRequest` now supports optional `query_id`, `original_query`,
`retrieval_query`, and `language` fields while retaining `query` as the
backward-compatible required retrieval text. The retrieval layer must consume
the single canonical processed field agreed with Ahmed; it must not guess
between original, normalized, and rewritten values.

`RetrievedChunk` supports `model_identifier` in addition to chunk/document
IDs, text, source metadata, rank, score, and retrieval method. These fields
are sufficient for Hassan to build citations without retrieval changing the
RAG module.
