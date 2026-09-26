"""Multi-step skill flow: ask -> form -> submit -> radar -> ask again -> radar without the form.

The skill tool is replaced with a 2-question fake; the in-memory user stub keeps the profile.
"""
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.agent import orchestrator, stubs
from app.modules.agent.llm_client import LLMError
from app.modules.agent.types import RouteResult
from app.schemas.contract import (
    AgentResponse,
    AssessmentFormData,
    AssessmentOption,
    AssessmentQuestion,
    SkillScores,
    User,
)

FORM = AssessmentFormData(
    assessment_id="skill_v1",
    title="แบบทดสอบ",
    questions=[
        AssessmentQuestion(id=q, text=f"คำถาม {q}", options=[AssessmentOption(value=v, label=str(v)) for v in range(5)])
        for q in ("q1", "q2")
    ],
)
TEST_USER = User(id="stub-user", email="stub@example.com", name="Stub User", onboarded=True)


def fake_scores(answers) -> SkillScores:
    by_id = {a.question_id: a.value for a in answers}
    return SkillScores(frontend=by_id["q1"] * 25, backend=by_id["q2"] * 25, network=0, embedded=0, ai_data=0, cybersecurity=0)


@pytest.fixture
def client(monkeypatch) -> Generator[TestClient, None, None]:
    s = orchestrator.services
    for name in ("get_user_context", "get_or_create_conversation", "add_user_message", "add_assistant_message",
                 "get_recent_messages", "save_skill_profile", "get_latest_skill", "top_skills"):
        monkeypatch.setattr(s, name, getattr(stubs, name))
    monkeypatch.setattr(stubs, "_skills", {})
    monkeypatch.setattr(s, "get_assessment", lambda: FORM)
    monkeypatch.setattr(s, "calculate_skill", fake_scores)
    monkeypatch.setattr(orchestrator.generator, "explain_skill", lambda *a: "สรุปจาก LLM")
    monkeypatch.setattr(orchestrator.intent_router, "route", lambda *a: RouteResult(intent="skill_analysis", source="rule"))
    assert s.get_current_user not in app.dependency_overrides
    assert s.get_session not in app.dependency_overrides
    app.dependency_overrides[s.get_current_user] = lambda: TEST_USER
    app.dependency_overrides[s.get_session] = lambda: None
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.pop(s.get_current_user, None)
        app.dependency_overrides.pop(s.get_session, None)
        assert s.get_current_user not in app.dependency_overrides
        assert s.get_session not in app.dependency_overrides


def chat(client: TestClient, message: str, conversation_id: str | None = None) -> AgentResponse:
    response = client.post("/api/chat", json={"conversation_id": conversation_id, "message": message})
    assert response.status_code == 200
    return AgentResponse.model_validate(response.json())


def submit(client: TestClient, conversation_id: str, answers: list[tuple[str, int]], assessment_id: str = "skill_v1"):
    return client.post("/api/assessment/submit", json={
        "conversation_id": conversation_id,
        "assessment_id": assessment_id,
        "answers": [{"question_id": q, "value": v} for q, v in answers],
    })


def test_full_skill_flow(client) -> None:
    form = chat(client, "ช่วยวิเคราะห์ skill ของผม")
    assert form.response_type == "assessment_form"

    response = submit(client, form.conversation_id, [("q1", 4), ("q2", 2)])
    assert response.status_code == 200
    radar = AgentResponse.model_validate(response.json())
    assert (radar.response_type, radar.meta.tool) == ("skill_radar", "skill.calculate_skill")
    assert (radar.data.scores.frontend, radar.data.scores.backend) == (100, 50)
    assert radar.data.top_skills == ["frontend", "backend"]
    assert radar.conversation_id == form.conversation_id

    again = chat(client, "skill ผมเป็นยังไง", form.conversation_id)
    assert again.response_type == "skill_radar"
    assert again.data.scores == radar.data.scores

    history = stubs.get_recent_messages(None, form.conversation_id, limit=10)
    assert [m["role"] for m in history] == ["user", "assistant", "user", "assistant", "user", "assistant"]


def test_retake_returns_form(client) -> None:
    form = chat(client, "ประเมิน skill")
    submit(client, form.conversation_id, [("q1", 1), ("q2", 1)])
    retake = chat(client, "ขอทำแบบประเมิน skill ใหม่", form.conversation_id)
    assert retake.response_type == "assessment_form"
    assert "ทำแบบประเมินใหม่" in retake.message


def test_radar_without_llm(client, monkeypatch) -> None:
    def down(*a):
        raise LLMError("down")

    monkeypatch.setattr(orchestrator.generator, "explain_skill", down)
    radar = submit(client, "c1", [("q1", 4), ("q2", 0)]).json()
    assert radar["response_type"] == "skill_radar"
    assert "Frontend" in radar["data"]["summary"]


@pytest.mark.parametrize(
    ("answers", "assessment_id"),
    [
        ([("q1", 4)], "skill_v1"),                        # missing q2
        ([("q1", 4), ("q1", 3), ("q2", 1)], "skill_v1"),  # duplicate
        ([("q1", 4), ("q9", 1)], "skill_v1"),             # unknown question
        ([("q1", 4), ("q2", 1)], "skill_v0"),             # old form
    ],
)
def test_invalid_answers_rejected(client, answers, assessment_id) -> None:
    response = submit(client, "c1", answers, assessment_id)
    assert response.status_code == 422
    assert stubs.get_latest_skill(None, "stub-user") is None


def test_value_out_of_range_rejected(client) -> None:
    assert submit(client, "c1", [("q1", 5), ("q2", 1)]).status_code == 422


def test_tool_unavailable_is_error_response(client, monkeypatch) -> None:
    def unavailable():
        raise NotImplementedError

    monkeypatch.setattr(orchestrator.services, "get_assessment", unavailable)
    response = submit(client, "c1", [("q1", 1), ("q2", 1)])
    assert response.status_code == 200
    assert (response.json()["response_type"], response.json()["data"]["code"]) == ("error", "tool_failed")


def test_scoring_failure_is_error_response(client, monkeypatch) -> None:
    def broken(answers):
        raise ValueError("bad weights")

    monkeypatch.setattr(orchestrator.services, "calculate_skill", broken)
    body = submit(client, "c1", [("q1", 1), ("q2", 1)]).json()
    assert (body["response_type"], body["data"]["code"]) == ("error", "tool_failed")
