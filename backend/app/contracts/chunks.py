"""Chunk contracts produced by document processing."""

from uuid import UUID

from pydantic import Field

from app.contracts.common import IdentifiedModel, Metadata


class Chunk(IdentifiedModel):
    document_id: UUID
    text: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    metadata: Metadata = Field(default_factory=Metadata)
