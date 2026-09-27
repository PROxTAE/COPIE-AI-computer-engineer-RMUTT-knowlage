"""Tests for dynamic skill assessment generation, scoring, and context retention."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.agent import orchestrator, stubs
from app.modules.agent.dynamic_skill import (
    DYNAMIC_ASSESSMENTS,
    extract_skill_topic,
    format_user_skills_context,
    generate_dynamic_assessment_form,
)
from app.modules.agent.types import RouteResult
from app.schemas.contract import AgentResponse, SkillScores, User

TEST_USER = User(id="user-dynamic-1", email="dyn@example.com", name="Dynamic User", onboarded=True)


def test_extract_skill_topic():
    assert extract_skill_topic("สกิลทำอาหารของผมเก่งไหม") == ("ทำอาหาร", False)
    assert extract_skill_topic("อยากรู้ว่าสกิล Python ผมดีไหม") == ("Python", False)
    assert extract_skill_topic("ช่วยประเมิน skill ของผมหน่อย") == ("วิศวกรรมคอมพิวเตอร์", True)
    assert extract_skill_topic("ทักษะการทำขนมของผม") == ("ทำขนม", False)


def test_generate_dynamic_assessment_form():
    form = generate_dynamic_assessment_form("การทำอาหาร")
    assert form.assessment_id.startswith("dynamic_")
    assert len(form.questions) >= 3
    assert form.questions[0].options[0].value == 0
    assert form.questions[0].options[4].value == 4
    assert form.assessment_id in DYNAMIC_ASSESSMENTS


@pytest.fixture
def dynamic_client(monkeypatch):
    s = orchestrator.services
    for name in (
        "get_user_context",
        "get_or_create_conversation",
        "add_user_message",
        "add_assistant_message",
        "get_recent_messages",
        "save_skill_profile",
        "get_latest_skill",
        "get_all_user_skills",
        "get_skill_by_topic",
        "top_skills",
    ):
        monkeypatch.setattr(s, name, getattr(stubs, name))
    monkeypatch.setattr(stubs, "_skills", {})
    monkeypatch.setattr(stubs, "_user_skills_list", {})
    monkeypatch.setattr(orchestrator.generator, "explain_skill", lambda *a, **kw: "สรุป CPE")
    monkeypatch.setattr(orchestrator.generator, "explain_dynamic_skill", lambda *a, **kw: "สรุปการทำอาหารยอดเยี่ยม")
    monkeypatch.setattr(orchestrator.generator, "answer_skill_inquiry", lambda msg, ctx, *a, **kw: f"คุณมีทักษะทำอาหารที่ดีมาก ({ctx})")
    monkeypatch.setattr(orchestrator.intent_router, "route", lambda *a: RouteResult(intent="skill_analysis", source="rule"))

    app.dependency_overrides[s.get_current_user] = lambda: TEST_USER
    app.dependency_overrides[s.get_session] = lambda: None
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.pop(s.get_current_user, None)
        app.dependency_overrides.pop(s.get_session, None)


def test_full_dynamic_skill_lifecycle(dynamic_client):
    # 1. User asks about a new skill topic (e.g. cooking) which has not been evaluated yet
    res1 = dynamic_client.post("/api/chat", json={"message": "สกิลทำอาหารของผมเก่งไหม"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["response_type"] == "assessment_form"
    form = data1["data"]
    assert "ทำอาหาร" in form["title"]
    assert len(form["questions"]) >= 5
    assessment_id = form["assessment_id"]

    # 2. User submits answers for the dynamic assessment
    answers = [{"question_id": q["id"], "value": 3} for q in form["questions"]]
    res2 = dynamic_client.post(
        "/api/assessment/submit",
        json={
            "conversation_id": data1["conversation_id"],
            "assessment_id": assessment_id,
            "answers": answers,
        },
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["response_type"] == "skill_radar"
    assert "75/100" in data2["message"]
    assert data2["data"]["dimensions"] is not None
    assert len(data2["data"]["dimensions"]) >= 5
    assert data2["data"]["dimensions"][0]["score"] == 75

    # Verify stored profile in stubs
    stored_skills = stubs.get_all_user_skills(None, TEST_USER.id)
    assert len(stored_skills) >= 1
    assert any(s.topic == "ทำอาหาร" and s.score == 75 for s in stored_skills)

    # 3. Next turn: User asks again about this skill!
    # Instead of re-throwing the form or raw radar, AI answers conversationally using the skill as CONTEXT!
    res3 = dynamic_client.post(
        "/api/chat",
        json={"conversation_id": data1["conversation_id"], "message": "สรุปสกิลทำอาหารของผมให้ฟังหน่อย"},
    )
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["response_type"] == "text"
    assert "คุณมีทักษะทำอาหารที่ดีมาก" in data3["message"]
    assert "75/100" in data3["message"]
    # Action chips include options to see radar or retake
    action_labels = [a["label"] for a in data3["actions"]]
    assert any("Radar" in label for label in action_labels)
