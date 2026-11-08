"""Document contracts produced by ingestion."""

from datetime import date
from pydantic import Field, HttpUrl

from app.contracts.common import IdentifiedModel, Metadata


class Document(IdentifiedModel):
    title: str = Field(min_length=1)
    source_url: HttpUrl | None = None
    source_type: str
    language: str | None = None
    metadata: Metadata = Field(default_factory=Metadata)
    content: str | None = None
    publication_date: date | None = None
    version: str | None = None
