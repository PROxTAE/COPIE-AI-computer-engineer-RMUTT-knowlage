"""Database-backed conversation history used by the agent and history API."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.user.models import Conversation, Feedback, Message, utc_now
from app.schemas.contract import (
    AgentResponse,
    ChatMessage,
    ConversationDetail,
    ConversationSummary,
)


def _iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def get_or_create_conversation(
    db: Session,
    user_id: str,
    conversation_id: str | None,
    first_message: str,
) -> str:
    conversation = db.get(Conversation, conversation_id) if conversation_id else None
    if conversation is not None:
        if conversation.user_id != user_id:
            raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงบทสนทนานี้")
        return conversation.id

    conversation = Conversation(
        **({"id": conversation_id} if conversation_id else {}),
        user_id=user_id,
        title=first_message[:40],
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation.id


def add_user_message(db: Session, conversation_id: str, text: str) -> str:
    message = Message(conversation_id=conversation_id, role="user", content=text)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message.id


def add_assistant_message(db: Session, conversation_id: str, response: AgentResponse) -> None:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise LookupError(f"conversation not found: {conversation_id}")

    message = Message(
        id=response.message_id,
        conversation_id=conversation_id,
        role="assistant",
        response_json=response.model_dump_json(),
        response_type=response.response_type,
        intent=response.meta.intent,
        latency_ms=response.meta.latency_ms,
    )
    conversation.updated_at = utc_now()
    db.add(message)
    db.add(conversation)
    db.commit()


def get_recent_messages(db: Session, conversation_id: str, limit: int = 6) -> list[dict]:
    if limit <= 0:
        return []

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = list(reversed(db.exec(statement).all()))
    messages = []
    for row in rows:
        text = row.content
        if row.role == "assistant" and row.response_json is not None:
            text = AgentResponse.model_validate_json(row.response_json).message
        messages.append({"role": row.role, "text": text})
    return messages


def list_conversations(db: Session, user_id: str) -> list[ConversationSummary]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
    )
    return [
        ConversationSummary(id=row.id, title=row.title, updated_at=_iso_utc(row.updated_at))
        for row in db.exec(statement).all()
    ]


def get_conversation_detail(
    db: Session,
    user_id: str,
    conversation_id: str,
) -> ConversationDetail:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="ไม่พบบทสนทนานี้")
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงบทสนทนานี้")

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
    )
    rows = db.exec(statement).all()
    assistant_ids = [row.id for row in rows if row.role == "assistant"]
    feedback_by_message: dict[str, str] = {}
    if assistant_ids:
        feedback_statement = select(Feedback).where(
            Feedback.user_id == user_id,
            Feedback.message_id.in_(assistant_ids),
        )
        feedback_by_message = {
            row.message_id: row.rating for row in db.exec(feedback_statement).all()
        }

    messages: list[ChatMessage] = []
    for row in rows:
        created_at = _iso_utc(row.created_at)
        if row.role == "user":
            messages.append(
                ChatMessage(
                    id=row.id,
                    role="user",
                    content=row.content or "",
                    created_at=created_at,
                )
            )
            continue

        if row.response_json is None:
            raise ValueError(f"assistant message has no response_json: {row.id}")
        messages.append(
            ChatMessage(
                id=row.id,
                role="assistant",
                response=AgentResponse.model_validate_json(row.response_json),
                feedback=feedback_by_message.get(row.id),
                created_at=created_at,
            )
        )

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        messages=messages,
    )
