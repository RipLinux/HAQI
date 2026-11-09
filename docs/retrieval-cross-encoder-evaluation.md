# Cross-Encoder evaluation

**Status: VERIFIED / SYNTHETIC EVALUATION.**

Model: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`

- Revision: `1427fd652930e4ba29e8149678df786c240d8825`
- CPU initialization: 4.868 s
- Probe scores: MSA 2.776, Egyptian Arabic -0.256, English 3.403
- Probe throughput: 108.4 pairs/s

With the same 10-result candidate pool:

| Candidate embedding | Recall@5 | MRR@5 | nDCG@5 | Average total ms |
|---|---:|---:|---:|---:|
| E5 hybrid | 1.0000 | 0.7542 | 0.6332 | 74.67 |
| E5 hybrid + Cross-Encoder | 1.0000 | 0.9458 | 0.9175 | 265.17 |
| MiniLM hybrid | 0.9500 | 0.7446 | 0.7453 | 72.43 |
| MiniLM hybrid + Cross-Encoder | 0.9875 | 0.9292 | 0.9042 | 251.21 |

The reranker improved ranking metrics on this dataset, but it does not prove
Arabic or Egyptian production quality. Human review and a larger reviewed
corpus are required.
