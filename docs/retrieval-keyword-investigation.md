# Keyword search investigation

## Status

**VERIFIED / SYNTHETIC EVALUATION.** The previous zero-result behavior was
reproduced on the 50-chunk, 40-query synthetic dataset. The existing query
uses parameterized PostgreSQL `simple` Full-Text Search correctly; the zero is
not caused by unsafe SQL or result conversion.

The synthetic chunks contain generic category terms while several queries are
paraphrases or Egyptian expressions. PostgreSQL `simple` token matching has no
Arabic stemming, dialect understanding, or semantic matching. Therefore a
query can be valid and still produce no FTS rows. This finding must not be
generalized to reviewed production data.

## Required investigation matrix

The isolated benchmark should record `pg_ts_config` availability and compare:

1. Exact token/substring matching.
2. `simple` FTS.
3. `english` FTS for English-only text.
4. `pg_trgm` similarity only if the extension is already available and an
   isolated test demonstrates measurable benefit.

English stemming must never be described as Arabic stemming. Basic Arabic
character normalization, if later agreed with Ahmed, must be a separate
preprocessing boundary and must not silently alter names or legal terms.

## Integration recommendation

Keep the current parameterized FTS adapter as the canonical baseline and make
the configuration explicit. A future production adapter may use a precomputed
`tsvector` column and a GIN index after Maha confirms the schema. Query
normalization and rewriting remain Ahmed's responsibility; retrieval consumes
the agreed canonical query field.
