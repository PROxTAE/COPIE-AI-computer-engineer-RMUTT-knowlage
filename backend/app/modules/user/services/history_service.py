"""Phase 1 history compatibility stubs; persistence is added in the history slice."""

from uuid import uuid4

from sqlmodel import Session

from app.schemas.contract import AgentResponse


def get_or_create_conversation(
    db: Session,
    user_id: str,
    conversation_id: str | None,
    first_message: str,
) -> str:
    del db, user_id, first_message
    return conversation_id or str(uuid4())


def add_user_message(db: Session, conversation_id: str, text: str) -> str:
    del db, conversation_id, text
    return str(uuid4())


def add_assistant_message(db: Session, conversation_id: str, response: AgentResponse) -> None:
    del db, conversation_id, response


def get_recent_messages(db: Session, conversation_id: str, limit: int = 6) -> list[dict]:
    del db, conversation_id, limit
    return []
