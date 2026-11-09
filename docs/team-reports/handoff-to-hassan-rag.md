# Handoff to Hassan: RAG

Retrieval returns the processed query, top-k ranked results, Chunk and
Document IDs, text, score/rank, retrieval method, source metadata, and
evidence references. Please confirm the expected Retrieval Result contract,
candidate-pool size, whether raw and reranked results are both needed, and
the citation fields required by answer generation.

Also confirm how RAG should handle empty or weak retrieval. Anas retrieves and
ranks evidence; Hassan assembles context, generates answers, and validates
grounding.
