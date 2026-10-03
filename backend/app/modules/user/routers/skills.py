"""Authenticated skill profile endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.modules.user.auth.deps import get_current_user
from app.modules.user.database import get_session
from app.modules.user.services.skill_store import get_latest_skill
from app.schemas.contract import SkillProfile, User

router = APIRouter(prefix="/api/skills", tags=["skills"])
CurrentUser = Annotated[User, Depends(get_current_user)]
Database = Annotated[Session, Depends(get_session)]


@router.get("/me", response_model=SkillProfile)
def read_my_skill(user: CurrentUser, db: Database) -> SkillProfile:
    skill = get_latest_skill(db, user.id)
    if skill is None:
        raise HTTPException(status_code=404, detail="ยังไม่มีผลประเมิน skill")
    return skill
