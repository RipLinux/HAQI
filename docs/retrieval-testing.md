# Retrieval testing

Unit tests run without Docker, internet access, model downloads, or government
data. They cover deterministic embeddings, vector validation, RRF, no-op
reranking, and offline metrics.

From `backend/`, run:

```bash
uv run pytest tests/retrieval tests/contract -v
uv run ruff check app/modules/retrieval tests/retrieval
```

PostgreSQL integration tests should be added after Maha confirms the Chunk table
and session interface. They must use an isolated development database and verify
the `vector` extension, insertion, cosine ordering, and dimension failures.

Evaluation judgments are JSONL with `query_id`, `relevant_chunk_ids`, and
optional `relevance` grades. Results are JSONL with `query_id` and `retrieved`.
Synthetic examples are provided under `data/evaluation/`; they are not
government ground truth.
Run the offline evaluator with:

```bash
python scripts/evaluate_retrieval.py results.jsonl judgments.jsonl -k 10
```

The report uses macro-averaging across queries and returns zero for queries with
no relevant judgments. Real model and latency comparisons remain optional until
a reviewed dataset and model dependencies are available.
# Model comparison workflow

The controlled synthetic dataset is generated without network access:

```text
python scripts/generate_model_comparison_dataset.py
```

It creates 50 fictional chunks, 40 queries, and graded judgments in
`data/evaluation/model_comparison/`. Rows are machine-generated and pending
human review; they are not production government content.

Retrieval runners can write one JSONL result per query and summarize quality
and latency with:

```text
python scripts/benchmark_retrieval.py RESULTS.jsonl \
  data/evaluation/model_comparison/relevance_judgments.jsonl -k 5
```

The utility reports macro Recall, Precision, MRR, nDCG, average/P50/P95
latency, and Recall by language. Use the same query set and candidate pool
for vector, PostgreSQL Full-Text Search, hybrid, and actual Cross-Encoder
reranking comparisons.

Real model tests remain optional and must be isolated from the normal unit
suite. They require recording model revision, embedding dimensions, CPU
resource usage, and download/inference errors rather than substituting fake
metrics.

Hardening commands:

```text
python scripts/validate_model_comparison_dataset.py
python model-evaluation/run_keyword_matrix.py
python model-evaluation/run_postgres_retrieval_benchmark.py intfloat/multilingual-e5-small
python model-evaluation/run_postgres_retrieval_benchmark.py sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
python model-evaluation/log_hardening_mlflow.py
```

The two embedding commands use isolated PostgreSQL schemas. Their result
reports include Recall/Precision/MRR/nDCG at 5 and 10 and language-specific
latency percentiles.
