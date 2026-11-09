# Retrieval runtime validation

Validation was performed on 2026-11-08 using Windows 11, Python 3.14.3,
Docker Desktop 4.98.0, Docker Engine 29.9.2, WSL2, 20 CPUs, and approximately
7.6 GiB available to Docker. The host had 4.71 GiB free disk space, no NVIDIA
GPU, and no Hugging Face model cache.

## Infrastructure

- `docker compose config`: passed.
- PostgreSQL `pgvector/pgvector:pg16`: healthy.
- pgvector extension: version `0.8.7`.
- MLflow: version `2.17.2`, healthy at `http://localhost:5000/version`.
- Backend: healthy at `http://localhost:8000/api/v1/health`.
- Frontend: reachable at `http://localhost:5173`.
- Named volumes: `haqi_postgres_data` and `haqi_mlflow_data`.

The initial MLflow image failed because MLflow 2.17.2 resolved SQLAlchemy 2.1,
which no longer exports `FallbackAsyncAdaptedQueuePool`. The image now pins
`SQLAlchemy>=2.0,<2.1`; rebuilding and restarting produced a healthy server.

## PostgreSQL and pgvector smoke test

An isolated `retrieval_runtime_test` schema was used with three 3-dimensional
vectors. Exact cosine search ranked the matching vector first with distance
`0.0`; dimension mismatch insertion was rejected; an HNSW cosine index was
created and returned the same ordering; metadata filtering returned the two
Arabic rows. After restarting PostgreSQL, all three rows, the extension, and
nearest-neighbor ordering remained available.

## MLflow persistence test

Experiment `HAQI-Retrieval-Runtime-Validation` was created with run
`837a1d754159479f86677f8a02087ae0`. The run contains eight parameters, six
metrics, and an `evaluation_report.json` artifact. The run and artifact were
retrieved successfully after restarting MLflow without removing its volume.

## Retrieval comparison

The following smoke comparison used two synthetic queries and the isolated
three-row PostgreSQL dataset. It validates wiring and score calculations only;
it is not a quality claim about government retrieval. “Hybrid + reranking” uses
the explicit `NoOpReranker`, not a CrossEncoder.

| Method | Recall@5 | Precision@5 | MRR@5 | nDCG@5 | Average latency (ms) |
|---|---:|---:|---:|---:|---:|
| Vector search | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 24.342 |
| Keyword search | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 2.809 |
| Hybrid search | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 0.204 |
| Hybrid + no-op reranking | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 0.053 |

The sample is too small for meaningful p95 latency or model selection. Real
embedding and CrossEncoder evaluation was not performed: `torch`,
`sentence-transformers`, and `transformers` are not installed, there is no GPU,
and only 4.71 GiB of disk was available. No model was downloaded.
