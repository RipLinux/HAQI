
"""Provider-independent LLM interface."""

from typing import Protocol


class LLMProvider(Protocol):
    """Common interface for language model providers."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a text response from the supplied prompts."""
        ...
