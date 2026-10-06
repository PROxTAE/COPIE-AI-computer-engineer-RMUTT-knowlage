"""Managing chat history: rename, delete, and grouping conversations into projects."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy import inspect, text
from sqlmodel import Session, select

from app.modules.user import database
from app.modules.user.models import Conversation, Feedback, Message
from app.modules.user.services.history_service import add_assistant_message, add_user_message
from app.modules.user.tests.test_remaining_user_api import (  # noqa: F401 - fixture
    Api,
    api,
    conversation,
    response_for,
)

NOW = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)


def owner_with_chat(api: Api, room: str = "room-1") -> tuple[dict, dict[str, str]]:
    owner, headers = api.login("owner@example.com")
    with Session(api.engine) as db:
        conversation(db, owner["user"]["id"], room, NOW)
    return owner, headers


@pytest.mark.parametrize(
    ("method", "path", "json"),
    [
        ("patch", "/api/conversations/x", {"title": "t"}),
        ("delete", "/api/conversations/x", None),
        ("get", "/api/projects", None),
        ("post", "/api/projects", {"name": "p"}),
        ("patch", "/api/projects/x", {"name": "p"}),
        ("delete", "/api/projects/x", None),
    ],
)
def test_management_endpoints_require_authentication(api: Api, method: str, path: str, json) -> None:
    assert api.client.request(method, path, json=json).status_code == 401


# ---------- rename / delete ----------


def test_rename_keeps_list_order(api: Api) -> None:
    _, headers = owner_with_chat(api)
    response = api.client.patch("/api/conversations/room-1", json={"title": "  แผนเรียนปี 2  "}, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "แผนเรียนปี 2"
    listed = api.client.get("/api/conversations", headers=headers).json()
    assert listed[0]["title"] == "แผนเรียนปี 2"
    assert listed[0]["updated_at"] == "2026-10-01T08:00:00Z"


@pytest.mark.parametrize("title", ["", "   ", "x" * 81])
def test_rename_rejects_bad_titles(api: Api, title: str) -> None:
    _, headers = owner_with_chat(api)
    assert api.client.patch("/api/conversations/room-1", json={"title": title}, headers=headers).status_code == 422


def test_delete_removes_messages_and_feedback(api: Api) -> None:
    owner, headers = owner_with_chat(api)
    with Session(api.engine) as db:
        add_user_message(db, "room-1", "คำถาม")
        add_assistant_message(db, "room-1", response_for("room-1", "answer-1"))
    api.client.post(
        "/api/feedback",
        json={"message_id": "answer-1", "rating": "up", "reason": None, "comment": None},
        headers=headers,
    )

    assert api.client.delete("/api/conversations/room-1", headers=headers).status_code == 204
    assert api.client.get("/api/conversations/room-1", headers=headers).status_code == 404
    with Session(api.engine) as db:
        assert db.exec(select(Message)).all() == []
        assert db.exec(select(Feedback)).all() == []
        assert db.exec(select(Conversation)).all() == []


def test_cannot_rename_or_delete_someone_elses_chat(api: Api) -> None:
    owner_with_chat(api)
    _, other = api.login("other@example.com")
    assert api.client.patch("/api/conversations/room-1", json={"title": "x"}, headers=other).status_code == 403
    assert api.client.delete("/api/conversations/room-1", headers=other).status_code == 403
    assert api.client.delete("/api/conversations/missing", headers=other).status_code == 404


# ---------- projects ----------


def test_project_lifecycle(api: Api) -> None:
    _, headers = owner_with_chat(api)
    created = api.client.post("/api/projects", json={"name": " สายงาน AI "}, headers=headers)
    assert created.status_code == 201
    project = created.json()
    assert (project["name"], project["conversation_count"]) == ("สายงาน AI", 0)

    moved = api.client.patch("/api/conversations/room-1", json={"project_id": project["id"]}, headers=headers)
    assert moved.json()["project_id"] == project["id"]
    assert api.client.get("/api/projects", headers=headers).json()[0]["conversation_count"] == 1
    assert api.client.get("/api/conversations", headers=headers).json()[0]["project_id"] == project["id"]

    renamed = api.client.patch(f"/api/projects/{project['id']}", json={"name": "AI & Data"}, headers=headers)
    assert (renamed.json()["name"], renamed.json()["conversation_count"]) == ("AI & Data", 1)

    # Removing from the project needs an explicit null; leaving the field out changes nothing.
    assert api.client.patch("/api/conversations/room-1", json={"title": "ใหม่"}, headers=headers).json()["project_id"] == project["id"]
    assert api.client.patch("/api/conversations/room-1", json={"project_id": None}, headers=headers).json()["project_id"] is None


def test_deleting_a_project_keeps_its_chats(api: Api) -> None:
    _, headers = owner_with_chat(api)
    project = api.client.post("/api/projects", json={"name": "ชั่วคราว"}, headers=headers).json()
    api.client.patch("/api/conversations/room-1", json={"project_id": project["id"]}, headers=headers)

    assert api.client.delete(f"/api/projects/{project['id']}", headers=headers).status_code == 204
    assert api.client.get("/api/projects", headers=headers).json() == []
    chats = api.client.get("/api/conversations", headers=headers).json()
    assert [(c["id"], c["project_id"]) for c in chats] == [("room-1", None)]


def test_projects_are_private(api: Api) -> None:
    _, owner = owner_with_chat(api)
    _, other = api.login("other@example.com")
    project = api.client.post("/api/projects", json={"name": "ของฉัน"}, headers=owner).json()

    assert api.client.get("/api/projects", headers=other).json() == []
    assert api.client.patch(f"/api/projects/{project['id']}", json={"name": "x"}, headers=other).status_code == 404
    assert api.client.delete(f"/api/projects/{project['id']}", headers=other).status_code == 404
    # Someone else's project cannot be used as a target either.
    other_project = api.client.post("/api/projects", json={"name": "ของเขา"}, headers=other).json()
    moved = api.client.patch("/api/conversations/room-1", json={"project_id": other_project["id"]}, headers=owner)
    assert moved.status_code == 404


@pytest.mark.parametrize("name", ["", "   ", "x" * 61])
def test_project_name_is_validated(api: Api, name: str) -> None:
    _, headers = api.login("owner@example.com")
    assert api.client.post("/api/projects", json={"name": name}, headers=headers).status_code == 422


# ---------- migration ----------


def test_create_all_adds_project_column_to_an_old_database(tmp_path, monkeypatch) -> None:
    engine = sa_create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id VARCHAR PRIMARY KEY)"))
        connection.execute(text(
            "CREATE TABLE conversations (id VARCHAR PRIMARY KEY, user_id VARCHAR, title VARCHAR, "
            "created_at DATETIME, updated_at DATETIME)"
        ))
        connection.execute(text("INSERT INTO conversations VALUES ('old', 'u', 'เก่า', '2026-01-01', '2026-01-01')"))
    monkeypatch.setattr(database, "engine", engine)

    database.create_all()
    database.create_all()  # running again on every start must be harmless

    columns = {column["name"] for column in inspect(engine).get_columns("conversations")}
    assert "project_id" in columns
    with engine.connect() as connection:
        assert connection.execute(text("SELECT project_id FROM conversations WHERE id = 'old'")).scalar() is None
    engine.dispose()
