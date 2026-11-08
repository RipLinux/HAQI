"""Answer contracts."""

from uuid import UUID

from pydantic import Field

from app.contracts.common import ContractModel


class Citation(ContractModel):
    chunk_id: UUID
    source_url: str | None = None
    label: str | None = None


class Answer(ContractModel):
    text: str
    citations: list[Citation] = Field(default_factory=list)
    abstained: bool = False
    abstention_reason: str | None = None
