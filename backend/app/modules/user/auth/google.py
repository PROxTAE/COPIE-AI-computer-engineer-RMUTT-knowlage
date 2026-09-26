"""Verify Google ID tokens and extract the identity claims used by COPIE."""

from typing import TypedDict

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2 import id_token as google_id_token

from app.core.config import settings


class GoogleIdentity(TypedDict):
    sub: str
    email: str
    name: str
    picture: str | None


class GoogleAuthConfigurationError(RuntimeError):
    """Raised when Google Login is not configured for this application."""


class InvalidGoogleTokenError(ValueError):
    """Raised when Google cannot verify the token or required claims."""


def verify_google_id_token(token: str) -> GoogleIdentity:
    client_id = settings.google_client_id.strip()
    if not client_id:
        raise GoogleAuthConfigurationError("GOOGLE_CLIENT_ID must be configured")

    try:
        claims = google_id_token.verify_oauth2_token(token, Request(), client_id)
    except (GoogleAuthError, ValueError) as exc:
        raise InvalidGoogleTokenError("Google ID token verification failed") from exc

    sub = claims.get("sub")
    email = claims.get("email")
    name = claims.get("name")
    picture = claims.get("picture")
    if not all(isinstance(value, str) and value.strip() for value in (sub, email, name)):
        raise InvalidGoogleTokenError("Google ID token is missing required claims")
    if picture is not None and not isinstance(picture, str):
        raise InvalidGoogleTokenError("Google ID token contains an invalid picture claim")

    return {
        "sub": sub.strip(),
        "email": email.strip(),
        "name": name.strip(),
        "picture": picture,
    }
