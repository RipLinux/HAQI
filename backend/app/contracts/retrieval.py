"""Contracts exchanged by retrieval components."""

from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.contracts.common import ContractModel


class RetrievalMethod(StrEnum):
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    RERANKED = "reranked"


class RetrievalRequest(ContractModel):
    query: str = Field(min_length=1)
    query_id: UUID | None = None
    original_query: str | None = None
    retrieval_query: str | None = None
    language: str | None = None
    top_k: int = Field(default=10, ge=1, le=100)
    filters: dict[str, str] = Field(default_factory=dict)


class RetrievedChunk(ContractModel):
    chunk_id: UUID
    document_id: UUID
    score: float | None = None
    retrieval_method: RetrievalMethod | str
    text: str | None = None
    source_url: str | None = None
    rank: int | None = Field(default=None, ge=1)
    model_identifier: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class RankedRetrievalResults(ContractModel):
    query: str
    query_id: UUID | None = None
    language: str | None = None
    results: list[RetrievedChunk] = Field(default_factory=list)
    method: RetrievalMethod | str
    metadata: dict[str, str] = Field(default_factory=dict)
