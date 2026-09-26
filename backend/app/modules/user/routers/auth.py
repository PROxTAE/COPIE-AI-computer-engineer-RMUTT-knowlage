"""Development authentication endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.user.auth.google import (
    GoogleAuthConfigurationError,
    InvalidGoogleTokenError,
    verify_google_id_token,
)
from app.modules.user.auth.jwt import create_access_token
from app.modules.user.database import get_session
from app.modules.user.models import User as UserRow
from app.modules.user.services.user_service import (
    GoogleIdentityConflictError,
    to_contract_user,
    upsert_google_user,
)
from app.schemas.contract import AuthResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


class DevAuthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3)
    name: str = Field(min_length=1)


class GoogleAuthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_token: str


@router.post("/google", response_model=AuthResponse)
def google_login(
    req: GoogleAuthRequest,
    db: Annotated[Session, Depends(get_session)],
) -> AuthResponse:
    try:
        identity = verify_google_id_token(req.id_token)
        user, is_new_user = upsert_google_user(db, identity)
    except GoogleAuthConfigurationError as exc:
        raise HTTPException(status_code=503, detail="ยังไม่ได้ตั้งค่า Google Login") from exc
    except InvalidGoogleTokenError as exc:
        raise HTTPException(
            status_code=401,
            detail="ไม่สามารถยืนยันตัวตนด้วย Google ได้ กรุณาลองใหม่",
        ) from exc
    except GoogleIdentityConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail="อีเมลนี้เชื่อมกับบัญชีอื่นอยู่แล้ว",
        ) from exc

    return AuthResponse(
        access_token=create_access_token(user.id),
        user=to_contract_user(user),
        is_new_user=is_new_user,
    )


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
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            user = db.exec(select(UserRow).where(UserRow.email == email)).first()
            if user is None:
                raise
            is_new_user = False
            user.name = name
            db.commit()
    else:
        user.name = name
        db.commit()
    db.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.id),
        user=to_contract_user(user),
        is_new_user=is_new_user,
    )
