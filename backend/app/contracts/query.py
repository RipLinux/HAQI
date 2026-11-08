"""User query contracts."""

from pydantic import Field

from app.contracts.common import ContractModel


class UserQuery(ContractModel):
    text: str = Field(min_length=1)
    language: str | None = None
    conversation_id: str | None = None
