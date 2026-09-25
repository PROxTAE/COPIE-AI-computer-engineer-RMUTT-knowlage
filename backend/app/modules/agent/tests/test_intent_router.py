import sys
from types import ModuleType

import pytest

from app.modules.agent import intent_router
from app.modules.agent.intent_router import route
from app.modules.agent.llm_client import LLMError


def _llm_returns(monkeypatch, reply) -> None:
    def fake(system: str, prompt: str) -> dict:
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(intent_router, "generate_json", fake)


def _ml_returns(monkeypatch, intent: str, confidence: float) -> None:
    module = ModuleType("app.modules.intent_ml")
    module.predict_intent = lambda text: (intent, confidence)
    monkeypatch.setitem(sys.modules, "app.modules.intent_ml", module)
    monkeypatch.setattr(intent_router.settings, "use_local_intent", True)


def test_llm_route(monkeypatch) -> None:
    _llm_returns(monkeypatch, {"intent": "curriculum", "year": 2, "semester": 1, "course_query": None})
    result = route("ปี 2 เทอม 1 เรียนอะไร")
    assert (result.intent, result.year, result.semester, result.source) == ("curriculum", 2, 1, "llm")


def test_llm_error_falls_back_to_rule(monkeypatch) -> None:
    _llm_returns(monkeypatch, LLMError("timeout"))
    result = route("ปี 3 เทอม 2 มีวิชาอะไร")
    assert (result.intent, result.year, result.semester, result.source) == ("curriculum", 3, 2, "rule")


@pytest.mark.parametrize("reply", [{"intent": "weather"}, {"intent": "curriculum", "year": 9}, {}])
def test_invalid_llm_json_falls_back_to_rule(monkeypatch, reply: dict) -> None:
    _llm_returns(monkeypatch, reply)
    assert route("อยากประเมิน skill").source == "rule"


def test_prompt_includes_user_and_history(monkeypatch) -> None:
    seen = {}

    def fake(system: str, prompt: str) -> dict:
        seen["prompt"] = prompt
        return {"intent": "curriculum"}

    monkeypatch.setattr(intent_router, "generate_json", fake)
    route("เทอมหน้าล่ะ", "current_student", 2, [{"role": "user", "text": "ปี 2 เทอม 1 เรียนอะไร"}])
    assert "นักศึกษาปัจจุบัน" in seen["prompt"]
    assert "ชั้นปี 2" in seen["prompt"]
    assert "ปี 2 เทอม 1 เรียนอะไร" in seen["prompt"]


def test_ml_used_when_confident(monkeypatch) -> None:
    _ml_returns(monkeypatch, "curriculum", 0.93)
    _llm_returns(monkeypatch, AssertionError("LLM must not be called"))
    result = route("ปี 1 เทอม 2 เรียนอะไร")
    assert (result.intent, result.year, result.semester, result.source) == ("curriculum", 1, 2, "ml")


def test_ml_low_confidence_uses_llm(monkeypatch) -> None:
    _ml_returns(monkeypatch, "curriculum", 0.4)
    _llm_returns(monkeypatch, {"intent": "general"})
    assert route("สวัสดี").source == "llm"


def test_ml_ignored_when_flag_off(monkeypatch) -> None:
    _ml_returns(monkeypatch, "curriculum", 0.99)
    monkeypatch.setattr(intent_router.settings, "use_local_intent", False)
    _llm_returns(monkeypatch, {"intent": "general"})
    assert route("สวัสดี").source == "llm"
