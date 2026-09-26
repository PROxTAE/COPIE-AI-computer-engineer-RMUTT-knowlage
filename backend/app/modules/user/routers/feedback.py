"""Authenticated feedback endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.modules.user.auth.deps import get_current_user
from app.modules.user.database import get_session
from app.modules.user.services.feedback_service import save_feedback
from app.schemas.contract import FeedbackRequest, User

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
CurrentUser = Annotated[User, Depends(get_current_user)]
Database = Annotated[Session, Depends(get_session)]


@router.post("")
def write_feedback(request: FeedbackRequest, user: CurrentUser, db: Database) -> dict[str, bool]:
    save_feedback(db, user.id, request)
    return {"ok": True}
