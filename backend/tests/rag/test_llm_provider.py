
from app.modules.rag.llm import MockLLMProvider

def test_mock_provider_returns_configured_response() -> None:
    provider = MockLLMProvider(response="HAQI test answer")

    result = provider.generate("System prompt", "User prompt")

    assert result == "HAQI test answer"


def test_mock_provider_records_prompts() -> None:
    provider = MockLLMProvider()

    provider.generate("System rules", "User question")

    assert provider.last_system_prompt == "System rules"
    assert provider.last_user_prompt == "User question"


def test_mock_provider_exposes_generate_method() -> None:
    provider = MockLLMProvider()
    assert callable(provider.generate)