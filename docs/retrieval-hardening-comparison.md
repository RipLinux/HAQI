# E5, MiniLM, and Cross-Encoder comparison

**Status: SYNTHETIC EVALUATION / VERIFIED EXECUTION.** The benchmark used 50
synthetic chunks and 40 machine-generated judgments. Human review completion is
0%, so this is not a production model-selection decision.

| Configuration | Recall@5 | Precision@5 | MRR@5 | nDCG@5 | Recall@10 | MRR@10 | Avg ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| E5 vector | 1.0000 | 0.4000 | 0.7542 | 0.6332 | 1.0000 | 0.7542 | 73.00 |
| MiniLM vector | 0.9500 | 0.3800 | 0.7446 | 0.7453 | 0.9875 | 0.7446 | 70.64 |
| E5 hybrid | 1.0000 | 0.4000 | 0.7542 | 0.6332 | 1.0000 | 0.7542 | 74.67 |
| MiniLM hybrid | 0.9500 | 0.3800 | 0.7446 | 0.7453 | 0.9875 | 0.7446 | 72.43 |
| E5 hybrid + Cross-Encoder | 1.0000 | 0.4000 | 0.9458 | 0.9175 | 1.0000 | 0.9458 | 265.17 |
| MiniLM hybrid + Cross-Encoder | 0.9875 | 0.3950 | 0.9292 | 0.9042 | 0.9875 | 0.9292 | 251.21 |

Language-specific results are stored in:

- `model-evaluation/results/benchmark_report_e5.json`
- `model-evaluation/results/benchmark_report_minilm.json`

The E5 and MiniLM embeddings were isolated in
`retrieval_model_comparison_e5` and `retrieval_model_comparison_minilm`.
Vectors were never mixed.

## Interpretation

E5 is the stronger Recall@5 baseline here. MiniLM has higher baseline nDCG,
but lower recall. E5 reranking produced the highest observed MRR/nDCG, while
MiniLM reranking had slightly lower latency and slightly lower recall. These
are preliminary synthetic findings, not a final recommendation.
