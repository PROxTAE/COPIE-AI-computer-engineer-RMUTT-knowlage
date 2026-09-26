"""API coverage for the final P2 history, skill, feedback, and profile slice."""

from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.modules.agent import orchestrator
from app.modules.agent.router import router as agent_router
from app.modules.agent.types import RouteResult
from app.modules.user.database import get_session
from app.modules.user.models import Conversation, Feedback, Message, SkillProfileRow
from app.modules.user.models import User as UserRow
from app.modules.user.routers import router as user_router
from app.modules.user.services.history_service import add_assistant_message, add_user_message
from app.modules.user.services.skill_store import save_skill_profile
from app.schemas.contract import (
    AgentResponse,
    AssessmentAnswer,
    ConversationDetail,
    ConversationSummary,
    ResponseMeta,
    SkillProfile,
    SkillScores,
)


@dataclass
class Api:
    client: TestClient
    engine: object

    def login(self, email: str) -> tuple[dict, dict[str, str]]:
        response = self.client.post(
            "/api/auth/dev",
            json={"email": email, "name": email.split("@")[0]},
        )
        assert response.status_code == 200
        body = response.json()
        return body, {"Authorization": f"Bearer {body['access_token']}"}


@pytest.fixture
def api(monkeypatch) -> Generator[Api, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(user_router)
    app.include_router(agent_router)
    app.dependency_overrides[get_session] = test_session
    monkeypatch.setattr(settings, "jwt_secret", "remaining-user-api-test-secret-at-least-32-bytes")
    monkeypatch.setattr(settings, "dev_auth", True)
    with TestClient(app) as client:
        yield Api(client=client, engine=engine)
    engine.dispose()


def response_for(conversation_id: str, message_id: str, text: str = "คำตอบ") -> AgentResponse:
    return AgentResponse(
        conversation_id=conversation_id,
        message_id=message_id,
        message=text,
        response_type="text",
        data=None,
        meta=ResponseMeta(intent="general", tool=None, latency_ms=12),
    )


def conversation(db: Session, user_id: str, row_id: str, updated_at: datetime) -> Conversation:
    row = Conversation(id=row_id, user_id=user_id, title=f"ห้อง {row_id}", updated_at=updated_at)
    db.add(row)
    db.commit()
    return row


@pytest.mark.parametrize(
    ("method", "path", "json"),
    [
        ("get", "/api/conversations", None),
        ("get", "/api/conversations/missing", None),
        ("get", "/api/skills/me", None),
        ("post", "/api/feedback", {"message_id": "missing", "rating": "up", "reason": None, "comment": None}),
    ],
)
def test_new_endpoints_require_authentication(api: Api, method: str, path: str, json) -> None:
    response = api.client.request(method, path, json=json)
    assert response.status_code == 401


def test_conversation_list_empty_isolation_and_deterministic_order(api: Api) -> None:
    owner, owner_headers = api.login("owner@example.com")
    other, _ = api.login("other@example.com")
    assert api.client.get("/api/conversations", headers=owner_headers).json() == []

    same_time = datetime(2026, 9, 26, 8, 0, tzinfo=timezone.utc)
    newer = same_time + timedelta(hours=1)
    with Session(api.engine) as db:
        conversation(db, owner["user"]["id"], "a-room", same_time)
        conversation(db, owner["user"]["id"], "b-room", same_time)
        conversation(db, owner["user"]["id"], "newest-room", newer)
        conversation(db, other["user"]["id"], "foreign-room", newer + timedelta(hours=1))

    response = api.client.get("/api/conversations", headers=owner_headers)
    assert response.status_code == 200
    summaries = [ConversationSummary.model_validate(item) for item in response.json()]
    assert [item.id for item in summaries] == ["newest-room", "b-room", "a-room"]
    assert all(item.updated_at.endswith("Z") for item in summaries)


def test_conversation_detail_missing_and_foreign(api: Api) -> None:
    owner, owner_headers = api.login("owner@example.com")
    _, other_headers = api.login("other@example.com")
    with Session(api.engine) as db:
        conversation(db, owner["user"]["id"], "private-room", datetime.now(timezone.utc))

    assert api.client.get("/api/conversations/missing", headers=owner_headers).status_code == 404
    forbidden = api.client.get("/api/conversations/private-room", headers=other_headers)
    assert forbidden.status_code == 403


def test_conversation_detail_reconstructs_messages_and_current_user_feedback(api: Api) -> None:
    owner, owner_headers = api.login("owner@example.com")
    other, _ = api.login("other@example.com")
    owner_id = owner["user"]["id"]
    with Session(api.engine) as db:
        room = conversation(db, owner_id, "history-room", datetime.now(timezone.utc))
        user_id = add_user_message(db, room.id, "คำถามแรก")
        assistant = response_for(room.id, "assistant-one")
        add_assistant_message(db, room.id, assistant)
        second_user_id = add_user_message(db, room.id, "คำถามต่อ")

        base = datetime(2026, 9, 26, 5, 0, tzinfo=timezone.utc)
        for index, message_id in enumerate((user_id, assistant.message_id, second_user_id)):
            row = db.get(Message, message_id)
            row.created_at = base + timedelta(minutes=index)
            db.add(row)
        db.add(Feedback(message_id=assistant.message_id, user_id=owner_id, rating="down", reason="incomplete"))
        db.add(Feedback(message_id=assistant.message_id, user_id=other["user"]["id"], rating="up"))
        db.commit()

    response = api.client.get("/api/conversations/history-room", headers=owner_headers)
    assert response.status_code == 200
    detail = ConversationDetail.model_validate(response.json())
    assert [message.id for message in detail.messages] == [user_id, assistant.message_id, second_user_id]
    assert all(message.created_at.endswith("Z") for message in detail.messages)
    assert detail.messages[0].content == "คำถามแรก"
    assert detail.messages[1].response == assistant
    assert detail.messages[1].feedback == "down"
    assert detail.messages[2].content == "คำถามต่อ"


def test_conversation_detail_has_null_feedback_when_unrated(api: Api) -> None:
    owner, headers = api.login("owner@example.com")
    with Session(api.engine) as db:
        room = conversation(db, owner["user"]["id"], "unrated-room", datetime.now(timezone.utc))
        add_assistant_message(db, room.id, response_for(room.id, "unrated-answer"))

    detail = api.client.get("/api/conversations/unrated-room", headers=headers).json()
    assert detail["messages"][0]["feedback"] is None


def test_history_routes_are_mounted_in_openapi(api: Api) -> None:
    paths = set(api.client.app.openapi()["paths"])
    assert {"/api/conversations", "/api/conversations/{conversation_id}"} <= paths


def test_chat_history_can_be_listed_loaded_and_continued(api: Api, monkeypatch) -> None:
    _, headers = api.login("chat@example.com")
    monkeypatch.setattr(
        orchestrator.intent_router,
        "route",
        lambda *args: RouteResult(intent="clarify", source="rule"),
    )

    first = api.client.post(
        "/api/chat",
        headers=headers,
        json={"conversation_id": None, "message": "คำถามแรก"},
    )
    assert first.status_code == 200
    conversation_id = first.json()["conversation_id"]
    assert [item["id"] for item in api.client.get("/api/conversations", headers=headers).json()] == [conversation_id]
    before = api.client.get(f"/api/conversations/{conversation_id}", headers=headers).json()
    assert [message["role"] for message in before["messages"]] == ["user", "assistant"]

    continued = api.client.post(
        "/api/chat",
        headers=headers,
        json={"conversation_id": conversation_id, "message": "ถามต่อ"},
    )
    assert continued.status_code == 200
    after = api.client.get(f"/api/conversations/{conversation_id}", headers=headers).json()
    assert [message["role"] for message in after["messages"]] == ["user", "assistant", "user", "assistant"]

    _, second_headers = api.login("second@example.com")
    assert api.client.get("/api/conversations", headers=second_headers).json() == []
    assert api.client.get(f"/api/conversations/{conversation_id}", headers=second_headers).status_code == 403


def scores(frontend: int) -> SkillScores:
    return SkillScores(
        frontend=frontend,
        backend=60,
        network=50,
        embedded=40,
        ai_data=30,
        cybersecurity=20,
    )


def test_skill_endpoint_returns_latest_and_never_another_users_profile(api: Api) -> None:
    owner, owner_headers = api.login("owner@example.com")
    other, other_headers = api.login("other@example.com")
    answer = [AssessmentAnswer(question_id="q1", value=4)]
    with Session(api.engine) as db:
        save_skill_profile(db, other["user"]["id"], scores(10), answer)

    assert api.client.get("/api/skills/me", headers=owner_headers).status_code == 404
    with Session(api.engine) as db:
        save_skill_profile(db, owner["user"]["id"], scores(20), answer)
        expected = save_skill_profile(db, owner["user"]["id"], scores(90), answer)

    response = api.client.get("/api/skills/me", headers=owner_headers)
    assert response.status_code == 200
    assert SkillProfile.model_validate(response.json()) == expected
    assert SkillProfile.model_validate(api.client.get("/api/skills/me", headers=other_headers).json()).scores.frontend == 10


def feedback_room(api: Api) -> tuple[dict[str, str], str, str, str]:
    owner, headers = api.login("feedback@example.com")
    with Session(api.engine) as db:
        room = conversation(db, owner["user"]["id"], "feedback-room", datetime.now(timezone.utc))
        user_message_id = add_user_message(db, room.id, "คำถาม")
        assistant_id = "feedback-answer"
        add_assistant_message(db, room.id, response_for(room.id, assistant_id))
    return headers, owner["user"]["id"], user_message_id, assistant_id


def post_feedback(api: Api, headers: dict[str, str], message_id: str, **overrides):
    body = {"message_id": message_id, "rating": "up", "reason": None, "comment": None}
    body.update(overrides)
    return api.client.post("/api/feedback", headers=headers, json=body)


def test_feedback_insert_update_and_history_round_trip(api: Api) -> None:
    headers, user_id, _, assistant_id = feedback_room(api)
    assert post_feedback(api, headers, assistant_id).json() == {"ok": True}
    down = post_feedback(
        api,
        headers,
        assistant_id,
        rating="down",
        reason="incomplete",
        comment="อยากได้รายละเอียดเพิ่ม",
    )
    assert down.json() == {"ok": True}

    with Session(api.engine) as db:
        rows = db.exec(select(Feedback).where(Feedback.user_id == user_id)).all()
        assert len(rows) == 1
        assert (rows[0].rating, rows[0].reason, rows[0].comment) == (
            "down",
            "incomplete",
            "อยากได้รายละเอียดเพิ่ม",
        )

    assert post_feedback(api, headers, assistant_id).json() == {"ok": True}
    with Session(api.engine) as db:
        rows = db.exec(select(Feedback).where(Feedback.user_id == user_id)).all()
        assert len(rows) == 1
        assert (rows[0].rating, rows[0].reason, rows[0].comment) == ("up", None, None)

    detail = api.client.get("/api/conversations/feedback-room", headers=headers).json()
    assistant = next(message for message in detail["messages"] if message["role"] == "assistant")
    assert assistant["feedback"] == "up"


def test_feedback_missing_foreign_and_user_message_rejected(api: Api) -> None:
    headers, _, user_message_id, assistant_id = feedback_room(api)
    _, other_headers = api.login("feedback-other@example.com")

    assert post_feedback(api, headers, "missing").status_code == 404
    assert post_feedback(api, other_headers, assistant_id).status_code == 403
    assert post_feedback(api, headers, user_message_id).status_code == 400


@pytest.mark.parametrize(
    "overrides",
    [
        {"rating": "sideways"},
        {"rating": "down", "reason": "not-a-reason"},
        {"rating": "down", "comment": "x" * 501},
    ],
)
def test_feedback_contract_validation(api: Api, overrides: dict) -> None:
    headers, _, _, assistant_id = feedback_room(api)
    assert post_feedback(api, headers, assistant_id, **overrides).status_code == 422


@pytest.mark.parametrize(
    ("user_type", "study_year", "expected"),
    [
        ("current_student", None, 422),
        ("near_graduate", None, 422),
        ("prospective", 1, 422),
        ("current_student", 2, 200),
        ("near_graduate", 4, 200),
        ("prospective", None, 200),
    ],
)
def test_profile_study_year_combinations(
    api: Api,
    user_type: str,
    study_year: int | None,
    expected: int,
) -> None:
    _, headers = api.login(f"{user_type}-{study_year}@example.com")
    response = api.client.put(
        "/api/users/me/profile",
        headers=headers,
        json={
            "display_name": "ผู้ทดสอบ",
            "age_range": "21_23",
            "user_type": user_type,
            "study_year": study_year,
        },
    )
    assert response.status_code == expected
