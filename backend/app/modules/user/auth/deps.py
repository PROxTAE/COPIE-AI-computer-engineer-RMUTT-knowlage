"""FastAPI dependencies for authenticated user endpoints."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.modules.user.auth.jwt import decode_access_token
from app.modules.user.database import get_session
from app.modules.user.models import User as UserRow
from app.modules.user.services.user_service import to_contract_user
from app.schemas.contract import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/dev", auto_error=False)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_session)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="ไม่สามารถยืนยันตัวตนได้ กรุณาเข้าสู่ระบบใหม่",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_error
    try:
        user_id = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise credentials_error from exc

    user = db.get(UserRow, user_id)
    if user is None:
        raise credentials_error
    return to_contract_user(user)
