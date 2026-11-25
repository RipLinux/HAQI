"""Public API request and response schemas."""

from app.contracts.answers import Answer
from app.contracts.common import ContractModel
from app.contracts.query import UserQuery


class ChatRequest(ContractModel):
    query: UserQuery


class ChatResponse(ContractModel):
    answer: Answer


class HealthResponse(ContractModel):
    status: str
    service: str
    version: str
