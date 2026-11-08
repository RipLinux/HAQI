# Architecture

The React frontend calls the FastAPI API. The initial backend exposes process health and explicit 501 scaffolds for chat and services. PostgreSQL with pgvector is the durable store; MLflow stores experiment metadata and artifacts. Ingestion, Arabic NLP, retrieval, and RAG folders are ownership boundaries for future work, not implemented business logic. The planned flow is query understanding -> hybrid retrieval -> evidence validation -> grounded answer.
