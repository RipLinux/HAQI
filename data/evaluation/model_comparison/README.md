# Model comparison dataset

This directory is a controlled, fictional benchmark for comparing retrieval
implementations. Every document is synthetic and must not be presented as a
real government policy, fee, eligibility rule, or procedure.

The files are generated deterministically by:

```text
python scripts/generate_model_comparison_dataset.py
```

The generator creates 50 chunks and 40 queries across Arabic MSA, Egyptian
Arabic, and English. Judgments use grades `0` (not relevant), `1` (partial),
and `2` (highly relevant). All rows are marked `machine_generated` and
`pending_human_review`; these data must be reviewed before model-selection
decisions.

Files:

- `synthetic_chunks.jsonl`: fictional chunk text and citation-shaped metadata.
- `synthetic_queries.jsonl`: benchmark queries and language/category labels.
- `relevance_judgments.jsonl`: explicit graded relevance judgments.
- `dataset_metadata.json`: version, counts, generation policy, and limitations.
