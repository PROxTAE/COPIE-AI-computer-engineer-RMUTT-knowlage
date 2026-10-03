"""Authenticated user endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.modules.user.auth.deps import get_current_user
from app.modules.user.database import get_session
from app.modules.user.services.user_service import update_profile
from app.schemas.contract import ProfileUpdate, User

router = APIRouter(prefix="/api/users", tags=["users"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=User)
def read_me(user: CurrentUser) -> User:
    return user


@router.put("/me/profile", response_model=User)
def write_profile(
    profile: ProfileUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_session)],
) -> User:
    needs_study_year = profile.user_type in ("current_student", "near_graduate")
    if needs_study_year and profile.study_year is None:
        raise HTTPException(status_code=422, detail="กรุณาระบุชั้นปีสำหรับสถานะนักศึกษา")
    if profile.user_type == "prospective" and profile.study_year is not None:
        raise HTTPException(status_code=422, detail="ผู้สนใจเข้าศึกษาไม่ต้องระบุชั้นปี")
    return update_profile(db, user.id, profile)
