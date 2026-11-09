# ADR 0001: Retrieval baseline

- **Status:** provisional
- **Decision:** begin with cosine similarity, PostgreSQL full-text search using
  the `simple` configuration, RRF fusion with constant 60, and an explicit
  no-op reranker.
- **Reason:** these choices are dependency-light, deterministic, and easy to
  benchmark while Arabic NLP, the canonical Chunk mapping, and the embedding
  model remain open.
- **Follow-up:** evaluate HNSW, Arabic lexical strategies, model candidates,
  and CrossEncoder reranking on reviewed judgments before production selection.
