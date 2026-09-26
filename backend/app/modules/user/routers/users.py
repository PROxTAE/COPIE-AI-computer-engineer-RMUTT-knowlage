"""Authenticated user endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
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
    return update_profile(db, user.id, profile)
