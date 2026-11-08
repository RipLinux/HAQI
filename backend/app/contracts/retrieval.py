"""Retrieval output contracts."""

from uuid import UUID

from app.contracts.common import ContractModel


class RetrievedChunk(ContractModel):
    chunk_id: UUID
    document_id: UUID
    score: float | None = None
    retrieval_method: str
    text: str | None = None
    source_url: str | None = None
