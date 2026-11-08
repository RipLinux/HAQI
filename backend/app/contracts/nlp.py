"""NLP output contracts."""

from pydantic import Field

from app.contracts.common import ContractModel


class Entity(ContractModel):
    text: str
    label: str


class NlpOutput(ContractModel):
    intent: str | None = None
    entities: list[Entity] = Field(default_factory=list)
    normalized_query: str
    rewritten_query: str | None = None
    clarification_needed: bool = False
    clarification_question: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
