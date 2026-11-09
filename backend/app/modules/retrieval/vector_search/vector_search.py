"""Provider-to-store semantic search orchestration."""

from app.contracts.retrieval import RetrievalRequest, RetrievedChunk
from app.modules.retrieval.embeddings.base import EmbeddingProvider

from .store import VectorStore


class VectorSearcher:
    def __init__(self, provider: EmbeddingProvider, store: VectorStore) -> None:
        self.provider = provider
        self.store = store

    async def search(self, request: RetrievalRequest) -> list[RetrievedChunk]:
        vector = self.provider.embed_query(request.query)
        return await self.store.search(vector, request.top_k, request.filters)
