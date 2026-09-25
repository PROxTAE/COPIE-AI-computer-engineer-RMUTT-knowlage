"""Database schema and Phase 1 public-service tests."""

import inspect

from sqlalchemy import UniqueConstraint
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.modules.user import (
    add_assistant_message,
    add_user_message,
    get_latest_skill,
    get_or_create_conversation,
    get_recent_messages,
    get_user_context,
    save_skill_profile,
)
from app.modules.user.models import Feedback
from app.modules.user.models import User as UserRow
from app.schemas.contract import AssessmentAnswer, SkillScores


def make_session() -> Session:
    engine = create_engine("sqlite://", poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_database_contains_the_five_contract_tables() -> None:
    expected = {"users", "conversations", "messages", "skill_profiles", "feedback"}
    assert expected <= set(SQLModel.metadata.tables)
    constraints = Feedback.__table__.constraints
    assert any(
        isinstance(constraint, UniqueConstraint)
        and {column.name for column in constraint.columns} == {"message_id", "user_id"}
        for constraint in constraints
    )


def test_get_user_context_returns_contract_user_and_empty_skill() -> None:
    with make_session() as db:
        row = UserRow(email="student@example.com", name="Student")
        db.add(row)
        db.commit()
        db.refresh(row)

        context = get_user_context(db, row.id)

    assert context["user"].id == row.id
    assert context["user"].email == "student@example.com"
    assert context["skill"] is None


def test_history_stubs_have_contract_signatures_and_safe_values() -> None:
    assert list(inspect.signature(get_or_create_conversation).parameters) == [
        "db",
        "user_id",
        "conversation_id",
        "first_message",
    ]
    conversation_id = get_or_create_conversation(None, "u1", None, "hello")
    assert get_or_create_conversation(None, "u1", conversation_id, "hello") == conversation_id
    assert isinstance(add_user_message(None, conversation_id, "hello"), str)
    assert add_assistant_message(None, conversation_id, None) is None
    assert get_recent_messages(None, conversation_id) == []


def test_skill_stubs_have_contract_signatures_and_typed_values() -> None:
    scores = SkillScores(
        frontend=80,
        backend=90,
        network=20,
        embedded=30,
        ai_data=70,
        cybersecurity=40,
    )
    profile = save_skill_profile(
        None,
        "u1",
        scores,
        [AssessmentAnswer(question_id="q1", value=4)],
    )
    assert profile.scores == scores
    assert profile.top_skills == ["backend", "frontend"]
    assert profile.taken_at.endswith("Z")
    assert get_latest_skill(None, "u1") is None
