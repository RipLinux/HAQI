# Shared data contracts

Pydantic v2 models in `backend/app/contracts` are the stable interfaces between modules. Ingestion produces `Document`; processing produces `Chunk`; NLP consumes `UserQuery` and produces `NlpOutput`; retrieval produces `RetrievedChunk`; RAG consumes `RagInput` and produces `RagOutput`; the API exposes `ChatRequest`, `ChatResponse`, and `HealthResponse`. `Answer` and `Citation` are the answer boundary consumed by the frontend.
