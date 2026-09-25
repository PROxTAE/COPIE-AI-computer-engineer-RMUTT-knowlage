"""SQLModel tables owned by the user module."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "age_range IS NULL OR age_range IN ('under_18', '18_20', '21_23', '24_plus')"
        ),
        CheckConstraint(
            "user_type IS NULL OR user_type IN ('prospective', 'current_student', 'near_graduate')"
        ),
        CheckConstraint("study_year IS NULL OR study_year BETWEEN 1 AND 4"),
    )

    id: str = Field(default_factory=new_id, primary_key=True)
    google_sub: str | None = Field(default=None, unique=True, index=True)
    email: str = Field(index=True)
    name: str
    picture_url: str | None = None
    display_name: str | None = None
    age_range: str | None = None
    user_type: str | None = None
    study_year: int | None = None
    onboarded: bool = False
    created_at: datetime = Field(default_factory=utc_now)


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=new_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (CheckConstraint("role IN ('user', 'assistant')"),)

    id: str = Field(default_factory=new_id, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: str
    content: str | None = None
    response_json: str | None = None
    response_type: str | None = None
    intent: str | None = None
    latency_ms: int | None = None
    created_at: datetime = Field(default_factory=utc_now, index=True)


class SkillProfileRow(SQLModel, table=True):
    __tablename__ = "skill_profiles"

    id: str = Field(default_factory=new_id, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    scores_json: str
    answers_json: str
    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("message_id", "user_id"),
        CheckConstraint("rating IN ('up', 'down')"),
    )

    id: str = Field(default_factory=new_id, primary_key=True)
    message_id: str = Field(foreign_key="messages.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    rating: str
    reason: str | None = None
    comment: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
