# Handoff to Mohamed Hussein: data ingestion

Retrieval needs a canonical processed Chunk and Document representation. Please
confirm the following before production indexing:

| Field | Requirement |
|---|---|
| Chunk ID and Document ID | Required, stable across re-indexing |
| Chunk text and chunk index | Required |
| Title, source identifier/URL, language | Optional where unavailable |
| Page/section references, metadata, version/content hash | To be agreed |

Please confirm the canonical field names, processed Chunk export format, and
how source metadata/citations are represented. Retrieval generates embeddings
and indexes processed chunks; it does not extract, clean, or chunk documents.

The synthetic dataset's `source_identifier` is only a citation-shaped example,
not real source data.
