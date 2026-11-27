"""OpenAI implementation of the HAQI LLM provider interface."""

import os
from typing import Any

from app.modules.rag.llm.base import LLMProvider


class OpenAIProvider:
    """Generate grounded responses using the OpenAI Chat Completions API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
        client: Any | None = None,
    ) -> None:
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if client is None and not resolved_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI provider")

        self.model = model or os.getenv("HAQI_LLM_MODEL", "gpt-4o-mini")

        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "The OpenAI package is required. Install the project requirements."
                ) from exc

            client = OpenAI(api_key=resolved_key, timeout=timeout)

        self.client = client

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response from system and user prompts."""

        if not system_prompt.strip() or not user_prompt.strip():
            raise ValueError("System and user prompts must not be empty")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise RuntimeError("OpenAI returned an invalid response structure") from exc

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenAI returned an empty response")

        return content.strip()


def create_llm_provider() -> LLMProvider | None:
    """Create the configured production provider; never select the mock implicitly."""

    provider_name = os.getenv("HAQI_LLM_PROVIDER", "disabled").strip().lower()

    if provider_name in ("", "disabled", "none"):
        return None

    if provider_name == "openai":
        return OpenAIProvider()

    raise ValueError(
        f"Unsupported HAQI_LLM_PROVIDER: {provider_name!r}. "
        "Supported values: disabled, openai."
    )
