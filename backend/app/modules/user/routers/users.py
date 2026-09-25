"""Authenticated user endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.user.auth.deps import get_current_user
from app.schemas.contract import User

router = APIRouter(prefix="/api/users", tags=["users"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=User)
def read_me(user: CurrentUser) -> User:
    return user
