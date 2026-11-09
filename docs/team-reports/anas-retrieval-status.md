# Anas retrieval status

## Scope

Anas owns retrieval interfaces, embedding adapters, vector/keyword/hybrid
ranking, reranking boundaries, evaluation utilities, and retrieval
documentation. Ingestion, Arabic NLP, central database models/sessions, RAG,
and frontend code remain owned by their respective teammates.

## Implemented and verified previously

- Shared retrieval contracts in `backend/app/contracts/retrieval.py`.
- Lazy Sentence Transformers and Cross-Encoder adapters.
- Deterministic fake embeddings for offline tests.
- pgvector adapter boundary and PostgreSQL Full-Text Search boundary.
- Stable RRF fusion, no-op reranker, metrics, and MLflow tracker.
- 16 existing tests passed; Ruff check and format check passed.
- Docker PostgreSQL/pgvector, MLflow, backend, and frontend runtime checks
  passed in the previous validation session.

## Added in this phase

- Deterministic synthetic model-comparison dataset generator:
  `scripts/generate_model_comparison_dataset.py`.
- Backend-independent quality/latency summarizer:
  `scripts/benchmark_retrieval.py`.
- Dataset metadata and review instructions under
  `data/evaluation/model_comparison/`.
- Model evaluation and benchmark protocols under `docs/`.
- Individual team handoff reports under `docs/team-reports/`.

## Phase 4 measured execution

An isolated CPU environment at `model-evaluation\.venv` used Python 3.14.3,
PyTorch 2.15.0+cpu, Transformers 5.22.2, Sentence Transformers 6.2.0, and
psycopg 3.3.8. E5-small loaded with 384-dimensional unit-normalized vectors;
MiniLM also loaded with 384-dimensional unit-normalized vectors. The mMARCO
Cross-Encoder loaded and scored all three language probes.

An isolated PostgreSQL schema indexed 50 synthetic chunks with E5 vectors and
ran 40 queries through vector search, actual `simple` Full-Text Search, RRF,
and real Cross-Encoder reranking. Overall E5 results were:

| Method | Recall@5 | Precision@5 | MRR@5 | nDCG@5 | Avg/P50/P95 ms |
|---|---:|---:|---:|---:|---:|
| Vector | 1.000 | 0.400 | 0.754 | 0.633 | 64.06 / 65.91 / 72.24 |
| Keyword | 0.000 | 0.000 | 0.000 | 0.000 | 2.16 / 1.88 / 3.21 |
| Hybrid | 1.000 | 0.400 | 0.754 | 0.633 | 66.24 / 68.27 / 74.25 |
| Real Cross-Encoder | 1.000 | 0.400 | 0.946 | 0.917 | 206.63 / 228.16 / 265.96 |

The judgments are machine-generated and pending human review. The FTS result
is a documented synthetic-data limitation, not a production claim.

MLflow experiment `HAQI-Retrieval-Model-Comparison-v1` was created with four
finished runs: `adbb4cc5bff14d558c21c1a7b9d92b7e`,
`b3068be6ae3b43e6ad0792f539dfb807`, `78ba0cee9a47492a95c8ea5d0f67e69d`,
and `08d171c9f8a04ad3a2c4f684cc3cda80`. Each has 11 parameters, 28 metrics,
and benchmark report/CSV artifacts.

Production Chunk ORM integration remains **WAITING FOR MAHA**. The model
quality recommendation remains **WAITING FOR HUMAN REVIEW**.

## Phase 5 hardening

Dataset validation is **VERIFIED**: 50 unique chunks, 40 unique queries,
40 judgments, no missing references or invalid grades, and 0% human review
completion. The review sheet is
`model-evaluation/results/dataset_review_sheet.csv`.

The keyword matrix is **SYNTHETIC EVALUATION**. Whole-query exact matching,
`simple` FTS, and PostgreSQL `arabic` FTS scored zero on this paraphrase-heavy
dataset. A measured token-overlap fallback achieved Recall@5 0.25 and
Recall@10 0.55 overall. `pg_trgm` is available but was not enabled.

MiniLM's separate PostgreSQL benchmark is **VERIFIED** in
`retrieval_model_comparison_minilm`. The full comparison and Cross-Encoder
results are in `docs/retrieval-hardening-comparison.md`.

The new MLflow experiment `HAQI-Retrieval-Hardening-v1` is **VERIFIED** with
seven finished runs listed in `docs/retrieval-mlflow-hardening-summary.md`.

## Reproduction

```text
python scripts/generate_model_comparison_dataset.py
python scripts/benchmark_retrieval.py RESULTS.jsonl data/evaluation/model_comparison/relevance_judgments.jsonl -k 5
python -m pytest backend/tests -v
python -m ruff check backend/app/modules/retrieval backend/tests
python -m ruff format --check backend/app/modules/retrieval backend/tests
```

Before sharing results, retain the model revisions, environment details,
MLflow run IDs, and the explicit pending-review status.
