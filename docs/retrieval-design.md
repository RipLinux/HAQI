# Retrieval design

Retrieval is an independent, dependency-injected module. A processed query is
embedded and sent to the pgvector adapter, while the normalized query is sent to
PostgreSQL full-text search. Their results are fused with Reciprocal Rank Fusion
(RRF), then optionally passed to a reranker before Hassan's RAG pipeline consumes
the ranked chunks.

## Components

- `embeddings`: provider protocol, deterministic offline fake provider, and lazy
  optional Sentence Transformers adapters.
- `vector_search`: pgvector validation, batch indexing boundary, and cosine
  similarity search. The score is `1 - cosine_distance`, so higher is better.
- `keyword_search`: parameterized PostgreSQL configuration, defaulting to
  `simple`. It does not claim Arabic stemming; Ahmed's normalized query is
  accepted. The hardening matrix showed token-overlap can provide a lexical
  fallback on the synthetic set, but it is not a replacement for Arabic NLP.
- `hybrid_search`: stable chunk-ID deduplication and deterministic RRF ordering.
- `reranking`: explicit `NoOpReranker` plus an optional lazy CrossEncoder adapter.
- `evaluation`: offline Recall@K, Precision@K, MRR@K, and nDCG@K.

The pgvector table and column names are provisional until Maha confirms the
canonical Chunk mapping. No retrieval component creates a database engine or ORM
model.

## Indexing

Exact cosine search is the safe initial baseline. HNSW can be evaluated after
the dataset size and selected embedding model are known; no arbitrary production
dimension or index parameters are committed here.
