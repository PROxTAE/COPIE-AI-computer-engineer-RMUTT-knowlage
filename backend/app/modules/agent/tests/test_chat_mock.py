from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.agent import services
from app.schemas.contract import AgentResponse, User

TEST_USER = User(id="mock-user", email="mock@example.com", name="Mock User", onboarded=True)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    assert services.get_current_user not in app.dependency_overrides
    assert services.get_session not in app.dependency_overrides
    app.dependency_overrides[services.get_current_user] = lambda: TEST_USER
    app.dependency_overrides[services.get_session] = lambda: None
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.pop(services.get_current_user, None)
        app.dependency_overrides.pop(services.get_session, None)
        assert services.get_current_user not in app.dependency_overrides
        assert services.get_session not in app.dependency_overrides


@pytest.mark.parametrize("kind", ["text", "course_table", "cards", "assessment_form", "skill_radar", "error"])
def test_mock_prefix_forces_response_type(client: TestClient, kind: str) -> None:
    response = client.post("/api/chat", json={"conversation_id": None, "message": f"mock:{kind}"})
    assert response.status_code == 200
    body = response.json()
    AgentResponse.model_validate(body)
    assert body["response_type"] == kind


def test_empty_message_rejected(client: TestClient) -> None:
    assert client.post("/api/chat", json={"conversation_id": None, "message": ""}).status_code == 422
