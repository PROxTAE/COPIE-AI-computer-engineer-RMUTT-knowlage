"""Development authentication endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.user.auth.jwt import create_access_token
from app.modules.user.database import get_session
from app.modules.user.models import User as UserRow
from app.modules.user.services.user_service import to_contract_user
from app.schemas.contract import AuthResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


class DevAuthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3)
    name: str = Field(min_length=1)


@router.post("/dev", response_model=AuthResponse)
def dev_login(req: DevAuthRequest, db: Annotated[Session, Depends(get_session)]) -> AuthResponse:
    if not settings.dev_auth:
        raise HTTPException(status_code=404, detail="ไม่พบ endpoint นี้")

    email = req.email.strip().lower()
    name = req.name.strip()
    if not email or not name:
        raise HTTPException(status_code=422, detail="กรุณาระบุ email และ name")

    user = db.exec(select(UserRow).where(UserRow.email == email)).first()
    is_new_user = user is None
    if user is None:
        user = UserRow(email=email, name=name)
        db.add(user)
    else:
        user.name = name
    db.commit()
    db.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.id),
        user=to_contract_user(user),
        is_new_user=is_new_user,
    )
