"""Database-backed conversation history used by the agent."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.user.models import Conversation, Message, utc_now
from app.schemas.contract import AgentResponse


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
