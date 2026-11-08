"""Common contract primitives."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Metadata(ContractModel):
    """Traceable metadata attached to a document or chunk."""

    source_url: str | None = None
    source_type: str | None = None
    language: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class IdentifiedModel(ContractModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime | None = None
