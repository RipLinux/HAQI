# Retrieval model evaluation

## Status

**Status: VERIFIED for CPU inference and an isolated PostgreSQL benchmark.**
The quality data is still **SYNTHETIC EVALUATION**: all judgments are
machine-generated and pending human review.

## Planned candidates

| Role | Model | Expected output | Encoding requirement |
|---|---|---:|---|
| Primary embedding | `intfloat/multilingual-e5-small` | 384 dimensions | `query: ` and `passage: ` prefixes |
| Comparison embedding | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Verify from model config | No E5 prefix assumption |
| Reranker | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | scalar pair score | query/passage pairs |

The exact revision, license, model size, initialization time, CPU memory, and
language scores must be recorded by the model-evaluation runner. Do not mix
embeddings from different models in one vector index.

## Measured model execution

| Model | Revision | Downloaded cache size | Dimensions | Init s | Query s | Passage s | Batch throughput |
|---|---|---:|---:|---:|---:|---:|---:|
| `intfloat/multilingual-e5-small` | `614241f622f53c4eeff9890bdc4f31cfecc418b3` | 470.44 MiB | 384 | 153.346 | 0.039 | 0.020 | 230.6 items/s |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | `e8f8c211226b894fcb81acc59f3b34ba3efd5f42` | 457.51 MiB | 384 | 2.281 | 0.023 | 0.022 | 299.7 items/s |
| `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | `1427fd652930e4ba29e8149678df786c240d8825` | 726.98 MiB cache | scalar score | 4.868 | 0.111 / 3 pairs | n/a | 108.4 pairs/s |

E5 query and passage vectors were generated with the required `query: ` and
`passage: ` prefixes and normalized to unit length. The three direct
Cross-Encoder probe scores were 2.776 (MSA), -0.256 (Egyptian), and 3.403
(English). These scores are not standalone quality metrics.

## Evaluation protocol

Use `data/evaluation/model_comparison/` after running
`python scripts/generate_model_comparison_dataset.py`. Compare vector,
PostgreSQL Full-Text Search, RRF hybrid, and hybrid plus the actual
Cross-Encoder over the same queries and candidate pool. Report Recall,
Precision, MRR, and graded nDCG at 5 and 10, separately for MSA, Egyptian
Arabic, and English.

The complete E5/MiniLM comparison is in
`docs/retrieval-hardening-comparison.md`. E5 and MiniLM use separate
model-specific PostgreSQL schemas and their vectors are never mixed.

## Current conclusion

The existing `FakeEmbeddingProvider` remains the deterministic unit-test
baseline. E5-small is **VERIFIED** for CPU loading and PostgreSQL vector
integration; the MiniLM baseline is **VERIFIED** for CPU loading. The
Cross-Encoder is **VERIFIED** for scoring and reranking. A production model
recommendation remains **WAITING FOR HUMAN REVIEW** of the synthetic judgments
and a reviewed dataset.
