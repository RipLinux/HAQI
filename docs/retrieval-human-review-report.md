# Human review dataset report

**Status: MACHINE_GENERATED / PENDING HUMAN REVIEW.**

Validation result:

- 50 unique chunks.
- 40 unique queries and 40 unique judgments.
- 0 duplicate IDs or judgments.
- 0 missing query or chunk references.
- 0 invalid relevance grades.
- 0 queries with no relevant chunks.
- Language distribution: 10 MSA, 10 Egyptian Arabic, 20 English.
- Human review completion: 0%.

Review sheet:
`model-evaluation/results/dataset_review_sheet.csv`

For each query, a reviewer should inspect the query language/category, candidate
chunk texts, current grade, and then fill `reviewer_notes` and
`corrected_relevance`. Do not change `review_status` to `human_reviewed`
without an actual reviewer approval. The synthetic chunks are fictional and
must never be used as official service information.

Known quality risks: all queries have exactly two relevant chunks, there are no
explicit no-result queries, and the synthetic text is repetitive. These make
the current benchmark useful for wiring and regression, but weak evidence for
production model selection.
