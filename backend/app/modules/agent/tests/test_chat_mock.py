import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.contract import AgentResponse

client = TestClient(app)


@pytest.mark.parametrize("kind", ["text", "course_table", "cards", "assessment_form", "skill_radar", "error"])
def test_mock_prefix_forces_response_type(kind: str) -> None:
    response = client.post("/api/chat", json={"conversation_id": None, "message": f"mock:{kind}"})
    assert response.status_code == 200
    body = response.json()
    AgentResponse.model_validate(body)
    assert body["response_type"] == kind


def test_empty_message_rejected() -> None:
    assert client.post("/api/chat", json={"conversation_id": None, "message": ""}).status_code == 422

