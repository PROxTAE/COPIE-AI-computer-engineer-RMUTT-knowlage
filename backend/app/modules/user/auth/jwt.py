"""Create and validate the application's short-lived JWT access tokens."""

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_DAYS = 7


def validate_jwt_secret() -> str:
    secret = settings.jwt_secret
    if not secret or secret == "change-me":
        raise RuntimeError("JWT_SECRET must be configured with a non-default value")
    return secret


def create_access_token(user_id: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_DAYS)
    return jwt.encode(
        {"sub": user_id, "exp": expires_at},
        validate_jwt_secret(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, validate_jwt_secret(), algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise jwt.InvalidTokenError("missing subject")
    return user_id
