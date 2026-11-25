"""Contracts at the boundary of the RAG pipeline."""

from pydantic import Field

from app.contracts.common import ContractModel
from app.contracts.query import UserQuery
from app.contracts.retrieval import RetrievedChunk


class RagInput(ContractModel):
    query: UserQuery
    context: list[RetrievedChunk] = Field(default_factory=list)


class RagOutput(ContractModel):
    answer_text: str
    context: list[RetrievedChunk] = Field(default_factory=list)
    abstained: bool = False
    abstention_reason: str | None = None
