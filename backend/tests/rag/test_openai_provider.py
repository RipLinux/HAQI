from types import SimpleNamespace

import pytest

from app.modules.rag.llm.openai_provider import OpenAIProvider, create_llm_provider


class FakeCompletions:
    def __init__(self, content="Grounded answer."):
        self.content = content
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.content)
                )
            ]
        )


class FakeClient:
    def __init__(self, content="Grounded answer."):
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


def test_openai_provider_uses_expected_model_and_prompts():
    client = FakeClient()
    provider = OpenAIProvider(
        api_key="test-key",
        model="test-model",
        client=client,
    )

    result = provider.generate("System rules", "User question")

    assert result == "Grounded answer."
    assert client.completions.kwargs["model"] == "test-model"
    assert client.completions.kwargs["messages"] == [
        {"role": "system", "content": "System rules"},
        {"role": "user", "content": "User question"},
    ]


def test_openai_provider_strips_response():
    provider = OpenAIProvider(client=FakeClient("  Answer  "))
    assert provider.generate("System", "Question") == "Answer"


def test_openai_provider_rejects_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIProvider()


@pytest.mark.parametrize(
    ("system_prompt", "user_prompt"),
    [("", "Question"), ("System", ""), (" ", "Question")],
)
def test_openai_provider_rejects_empty_prompts(system_prompt, user_prompt):
    provider = OpenAIProvider(client=FakeClient())

    with pytest.raises(ValueError, match="prompts must not be empty"):
        provider.generate(system_prompt, user_prompt)


def test_openai_provider_rejects_empty_response():
    provider = OpenAIProvider(client=FakeClient("   "))

    with pytest.raises(RuntimeError, match="empty response"):
        provider.generate("System", "Question")


def test_create_provider_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("HAQI_LLM_PROVIDER", raising=False)
    assert create_llm_provider() is None


def test_create_provider_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("HAQI_LLM_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="Unsupported"):
        create_llm_provider()
