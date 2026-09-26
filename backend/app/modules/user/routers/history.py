"""Authenticated conversation history endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.modules.user.auth.deps import get_current_user
from app.modules.user.database import get_session
from app.modules.user.services.history_service import (
    get_conversation_detail,
    list_conversations,
)
from app.schemas.contract import ConversationDetail, ConversationSummary, User

router = APIRouter(prefix="/api/conversations", tags=["history"])
CurrentUser = Annotated[User, Depends(get_current_user)]
Database = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[ConversationSummary])
def read_conversations(user: CurrentUser, db: Database) -> list[ConversationSummary]:
    return list_conversations(db, user.id)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def read_conversation(
    conversation_id: str,
    user: CurrentUser,
    db: Database,
) -> ConversationDetail:
    return get_conversation_detail(db, user.id, conversation_id)
