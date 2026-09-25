import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.contract import AgentResponse

client = TestClient(app)


def _chat(message: str, conversation_id: str | None = None) -> dict:
    response = client.post("/api/chat", json={"conversation_id": conversation_id, "message": message})
    assert response.status_code == 200
    body = response.json()
    AgentResponse.model_validate(body)
    return body


@pytest.mark.parametrize(
    ("message", "response_type", "intent"),
    [
        ("ปี 2 เทอม 1 เรียนอะไรบ้าง", "course_table", "curriculum"),
        ("เทอมหน้าเรียนไร", "text", "clarify"),
        ("อยากประเมิน skill", "assessment_form", "skill_analysis"),
        ("วิชา data structure เรียนอะไร", "cards", "course_detail"),
        ("ภาคคอมเรียนเกี่ยวกับอะไร", "text", "department_info"),
    ],
)
def test_keyword_routing(message: str, response_type: str, intent: str) -> None:
    body = _chat(message)
    assert body["response_type"] == response_type
    assert body["meta"]["intent"] == intent


def test_course_table_uses_year_and_semester() -> None:
    data = _chat("ปี 3 เทอม 2")["data"]
    assert (data["year"], data["semester"]) == (3, 2)
    assert data["total_credits"] == sum(c["credits"] for c in data["courses"])


@pytest.mark.parametrize("kind", ["text", "course_table", "cards", "assessment_form", "skill_radar", "error"])
def test_forced_response_type(kind: str) -> None:
    assert _chat(f"mock:{kind}")["response_type"] == kind


def test_keeps_conversation_id() -> None:
    assert _chat("สวัสดี", conversation_id="abc")["conversation_id"] == "abc"


def test_empty_message_rejected() -> None:
    assert client.post("/api/chat", json={"conversation_id": None, "message": ""}).status_code == 422


def test_assessment_submit_returns_radar() -> None:
    response = client.post(
        "/api/assessment/submit",
        json={"conversation_id": "abc", "assessment_id": "skill_v1", "answers": [{"question_id": "q1", "value": 3}]},
    )
    assert response.status_code == 200
    body = response.json()
    AgentResponse.model_validate(body)
    assert body["response_type"] == "skill_radar"
