"""Database schema and persistent public-service tests."""

import inspect
import json
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import UniqueConstraint
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.modules.user import (
    add_assistant_message,
    add_user_message,
    get_latest_skill,
    get_or_create_conversation,
    get_recent_messages,
    get_user_context,
    save_skill_profile,
)
from app.modules.user.models import Conversation, Feedback, Message, SkillProfileRow
from app.modules.user.models import User as UserRow
from app.schemas.contract import (
    AgentResponse,
    AssessmentAnswer,
    ResponseMeta,
    SkillScores,
)


def make_session() -> Session:
    engine = create_engine("sqlite://", poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def add_user(db: Session, email: str) -> UserRow:
    user = UserRow(email=email, name=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_response(conversation_id: str, message_id: str, text: str) -> AgentResponse:
    return AgentResponse(
        conversation_id=conversation_id,
        message_id=message_id,
        message=text,
        response_type="text",
        data=None,
        meta=ResponseMeta(intent="general", tool=None, latency_ms=17),
    )


def make_scores(*, backend: int, frontend: int) -> SkillScores:
    return SkillScores(
        frontend=frontend,
        backend=backend,
        network=20,
        embedded=30,
        ai_data=70,
        cybersecurity=40,
    )


def test_database_contains_the_five_contract_tables() -> None:
    expected = {"users", "conversations", "messages", "skill_profiles", "feedback"}
    assert expected <= set(SQLModel.metadata.tables)
    constraints = Feedback.__table__.constraints
    assert any(
        isinstance(constraint, UniqueConstraint)
        and {column.name for column in constraint.columns} == {"message_id", "user_id"}
        for constraint in constraints
    )
    assert UserRow.__table__.c.email.unique is True
    assert any(
        index.unique and {column.name for column in index.columns} == {"email"}
        for index in UserRow.__table__.indexes
    )


def test_get_user_context_returns_contract_user_and_empty_skill() -> None:
    with make_session() as db:
        row = add_user(db, "student@example.com")
        context = get_user_context(db, row.id)

    assert context["user"].id == row.id
    assert context["user"].email == "student@example.com"
    assert context["skill"] is None


def test_get_or_create_conversation_persists_reuses_and_checks_owner() -> None:
    with make_session() as db:
        owner = add_user(db, "owner@example.com")
        other = add_user(db, "other@example.com")

        conversation_id = get_or_create_conversation(db, owner.id, None, "a" * 45)
        row = db.get(Conversation, conversation_id)
        assert row is not None
        assert row.user_id == owner.id
        assert row.title == "a" * 40
        assert get_or_create_conversation(db, owner.id, conversation_id, "ignored") == conversation_id

        with pytest.raises(HTTPException) as exc_info:
            get_or_create_conversation(db, other.id, conversation_id, "forbidden")
        assert exc_info.value.status_code == 403


def test_get_or_create_conversation_uses_a_supplied_missing_id() -> None:
    with make_session() as db:
        owner = add_user(db, "owner@example.com")
        requested_id = str(uuid4())
        conversation_id = get_or_create_conversation(db, owner.id, requested_id, "hello")

        assert conversation_id == requested_id
        assert db.get(Conversation, conversation_id) is not None


def test_messages_persist_and_recent_messages_are_ordered_and_limited() -> None:
    with make_session() as db:
        owner = add_user(db, "owner@example.com")
        conversation_id = get_or_create_conversation(db, owner.id, None, "first")
        original_updated_at = db.get(Conversation, conversation_id).updated_at

        first_id = add_user_message(db, conversation_id, "first")
        response = make_response(conversation_id, "assistant-message", "second")
        assert add_assistant_message(db, conversation_id, response) is None
        third_id = add_user_message(db, conversation_id, "third")

        first = db.get(Message, first_id)
        assistant = db.get(Message, response.message_id)
        third = db.get(Message, third_id)
        assert first is not None and first.role == "user" and first.content == "first"
        assert third is not None and third.content == "third"
        assert assistant is not None
        assert assistant.role == "assistant"
        assert assistant.content is None
        assert AgentResponse.model_validate_json(assistant.response_json) == response
        assert assistant.response_type == "text"
        assert assistant.intent == "general"
        assert assistant.latency_ms == 17
        assert db.get(Conversation, conversation_id).updated_at >= original_updated_at

        assert get_recent_messages(db, conversation_id, limit=2) == [
            {"role": "assistant", "text": "second"},
            {"role": "user", "text": "third"},
        ]
        assert get_recent_messages(db, conversation_id, limit=0) == []


def test_public_history_signatures_remain_locked() -> None:
    assert list(inspect.signature(get_or_create_conversation).parameters) == [
        "db",
        "user_id",
        "conversation_id",
        "first_message",
    ]
    assert list(inspect.signature(add_user_message).parameters) == ["db", "conversation_id", "text"]
    assert list(inspect.signature(add_assistant_message).parameters) == [
        "db",
        "conversation_id",
        "response",
    ]
    assert list(inspect.signature(get_recent_messages).parameters) == ["db", "conversation_id", "limit"]
    assert inspect.signature(get_recent_messages).parameters["limit"].default == 6


def test_skill_profile_persists_and_latest_wins() -> None:
    answers = [AssessmentAnswer(question_id="q1", value=4)]
    with make_session() as db:
        user = add_user(db, "student@example.com")
        first_scores = make_scores(backend=90, frontend=80)
        second_scores = make_scores(backend=10, frontend=95)

        first = save_skill_profile(db, user.id, first_scores, answers)
        second = save_skill_profile(db, user.id, second_scores, answers)
        latest = get_latest_skill(db, user.id)
        rows = db.exec(
            select(SkillProfileRow).where(SkillProfileRow.user_id == user.id)
        ).all()

        assert first.scores == first_scores
        assert first.top_skills == ["backend", "frontend"]
        assert first.taken_at.endswith("Z")
        assert second.scores == second_scores
        assert latest == second
        assert len(rows) == 2
        assert json.loads(rows[0].scores_json) == first_scores.model_dump()
        assert json.loads(rows[0].answers_json) == [answer.model_dump() for answer in answers]
        assert rows[0].scores_json == json.dumps(
            first_scores.model_dump(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )


def test_public_skill_signatures_remain_locked() -> None:
    assert list(inspect.signature(save_skill_profile).parameters) == [
        "db",
        "user_id",
        "scores",
        "answers",
    ]
    assert list(inspect.signature(get_latest_skill).parameters) == ["db", "user_id"]
