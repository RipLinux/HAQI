
"""Offline mock provider for LLM tests."""

from app.modules.rag.llm.base import LLMProvider


class MockLLMProvider:
    """Deterministic provider that does not require an API key."""

    def __init__(self, response: str = "Mock answer.") -> None:
        self.response = response
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return a configured response and retain the received prompts."""

        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt

        return self.response
