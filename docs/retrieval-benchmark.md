# Retrieval benchmark

## Reproducible inputs

## Runtime

Windows 11, Python 3.14.3, 20 logical CPUs, 15.69 GiB physical RAM
(3.16 GiB available at final check), no CUDA GPU, Docker configured with
8,161,992,704 bytes (about 7.6 GiB). PostgreSQL used
`pgvector/pgvector:pg16`; MLflow server was version 2.17.2.

Generate the controlled 50-chunk/40-query dataset with:

```text
python scripts/generate_model_comparison_dataset.py
```

Each runner should write JSONL rows containing `query_id`, ordered
`retrieved`, `language`, and `latency_ms`. Summarize them with:

```text
python scripts/benchmark_retrieval.py RESULTS.jsonl \
  data/evaluation/model_comparison/relevance_judgments.jsonl -k 5
```

The benchmark utility reports macro quality, average/P50/P95 latency, and
Recall by language. Missing result rows are treated as empty retrievals.

## Required configurations

1. Vector search with one model-specific pgvector table.
2. PostgreSQL Full-Text Search using the documented `simple` configuration.
3. Vector plus FTS using deterministic RRF.
4. The same hybrid candidate pool reranked by the actual Cross-Encoder.

Measure query embedding, vector search, keyword search, RRF, reranking, and
complete-pipeline timings separately. Warm up before timing and use at least
30 queries before interpreting P95.

## Current evidence

The E5 benchmark used 50 indexed synthetic chunks and 40 queries, with 10
candidate results per retrieval branch and a dedicated HNSW vector index.
P95 is based on all 40 queries.

| Method | Language | Recall@5 | Precision@5 | MRR@5 | nDCG@5 | Avg ms | P50 ms | P95 ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Vector | Overall | 1.000 | 0.400 | 0.754 | 0.633 | 64.06 | 65.91 | 72.24 |
| PostgreSQL FTS (`simple`) | Overall | 0.000 | 0.000 | 0.000 | 0.000 | 2.16 | 1.88 | 3.21 |
| Hybrid RRF | Overall | 1.000 | 0.400 | 0.754 | 0.633 | 66.24 | 68.27 | 74.25 |
| Hybrid + mMARCO Cross-Encoder | Overall | 1.000 | 0.400 | 0.946 | 0.917 | 206.63 | 228.16 | 265.96 |

Language-specific Recall@5 was 1.000 for every method with vector candidates.
Reranked MRR/nDCG were respectively MSA `0.883/0.874`, Egyptian Arabic
`0.950/0.903`, and English `0.975/0.946`.

The FTS zero is an observed result of this synthetic query/text construction:
`simple` token matching does not perform Arabic stemming or semantic
paraphrase matching, and several query terms do not occur in the synthetic
chunks. It is not evidence that PostgreSQL FTS is generally unusable.

Artifacts are in `model-evaluation/results/`. MLflow experiment
`HAQI-Retrieval-Model-Comparison-v1` contains runs:

- Vector: `adbb4cc5bff14d558c21c1a7b9d92b7e`
- Keyword: `b3068be6ae3b43e6ad0792f539dfb807`
- Hybrid: `78ba0cee9a47492a95c8ea5d0f67e69d`
- Reranked: `08d171c9f8a04ad3a2c4f684cc3cda80`

These are **SYNTHETIC EVALUATION**, not production quality evidence.
