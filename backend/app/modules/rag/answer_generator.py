
"""Generate answers using a provider-independent LLM interface."""

from app.contracts.query import UserQuery
from app.modules.rag.context_builder import ContextBuildResult
from app.modules.rag.llm.base import LLMProvider
from app.modules.rag.prompt_builder import PromptBuilder


class AnswerGenerator:
    """Coordinate prompt building and LLM response generation."""

    def __init__(
        self,
        provider: LLMProvider,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self.provider = provider
        self.prompt_builder = prompt_builder or PromptBuilder()

    def generate(
        self,
        query: UserQuery,
        context: ContextBuildResult,
    ) -> str:
        """Generate an answer from the user query and retrieved context."""

        prompt = self.prompt_builder.build(query, context)

        response = self.provider.generate(
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
        )

        if not isinstance(response, str) or not response.strip():
            raise RuntimeError("LLM provider returned an empty or invalid response")

        return response.strip()
