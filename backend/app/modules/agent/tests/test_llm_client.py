from types import SimpleNamespace

import pytest

from app.modules.agent import llm_client
from app.modules.agent.llm_client import LLMError, generate_json, generate_text


class FakeModels:
    def __init__(self, replies: list) -> None:
        self.replies = list(replies)
        self.calls = 0

    def generate_content(self, **kwargs):
        self.calls += 1
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return SimpleNamespace(text=reply)


@pytest.fixture
def fake(monkeypatch):
    def install(*replies):
        models = FakeModels(replies)
        monkeypatch.setattr(llm_client, "_client", lambda: SimpleNamespace(models=models))
        return models

    return install


def test_generate_text(fake) -> None:
    fake("สวัสดีครับ")
    assert generate_text("sys", "hi") == "สวัสดีครับ"


def test_retries_once_then_succeeds(fake) -> None:
    models = fake(TimeoutError("slow"), "ok")
    assert generate_text("sys", "hi") == "ok"
    assert models.calls == 2


def test_gives_up_after_two_attempts(fake) -> None:
    models = fake(TimeoutError("slow"), TimeoutError("slow"))
    with pytest.raises(LLMError):
        generate_text("sys", "hi")
    assert models.calls == 2


def test_empty_reply_is_error(fake) -> None:
    fake("", "  ")
    with pytest.raises(LLMError):
        generate_text("sys", "hi")


def test_generate_json(fake) -> None:
    fake('{"intent": "curriculum", "year": 2}')
    assert generate_json("sys", "q") == {"intent": "curriculum", "year": 2}


def test_generate_json_strips_code_fence(fake) -> None:
    fake('```json\n{"intent": "general"}\n```')
    assert generate_json("sys", "q") == {"intent": "general"}


@pytest.mark.parametrize("reply", ["not json", "[1, 2]"])
def test_generate_json_rejects_bad_output(fake, reply: str) -> None:
    fake(reply)
    with pytest.raises(LLMError):
        generate_json("sys", "q")


def test_missing_api_key(monkeypatch) -> None:
    llm_client._client.cache_clear()
    monkeypatch.setattr(llm_client.settings, "gemini_api_key", "")
    with pytest.raises(LLMError):
        generate_text("sys", "hi")
