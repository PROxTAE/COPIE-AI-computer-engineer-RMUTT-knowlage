"""Google Login and Phase 2 profile API tests without live Google calls."""

from collections.abc import Generator
from unittest.mock import ANY, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.modules.user.auth.google import (
    InvalidGoogleTokenError,
    verify_google_id_token,
)
from app.modules.user.auth.jwt import decode_access_token
from app.modules.user.database import get_session
from app.modules.user.models import User as UserRow
from app.modules.user.routers import router
from app.modules.user.services.user_service import upsert_google_user
from app.schemas.contract import AuthResponse, User


@pytest.fixture
def client(monkeypatch) -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = test_session
    monkeypatch.setattr(settings, "jwt_secret", "google-login-test-secret-at-least-32-bytes")
    monkeypatch.setattr(settings, "google_client_id", "test-client.apps.googleusercontent.com")
    monkeypatch.setattr(settings, "dev_auth", True)
    with TestClient(app) as test_client:
        yield test_client


def google_identity(**overrides) -> dict[str, str | None]:
    identity: dict[str, str | None] = {
        "sub": "google-sub-1",
        "email": "Student@Example.com",
        "name": "Student Name",
        "picture": "https://example.com/avatar.png",
    }
    identity.update(overrides)
    return identity


def test_google_verifier_uses_configured_audience_without_requiring_email_verified(
    monkeypatch,
) -> None:
    verifier = MagicMock(return_value=google_identity())
    monkeypatch.setattr(settings, "google_client_id", "client-id.apps.googleusercontent.com")
    monkeypatch.setattr(
        "app.modules.user.auth.google.google_id_token.verify_oauth2_token",
        verifier,
    )

    identity = verify_google_id_token("google-id-token")

    assert identity == google_identity()
    verifier.assert_called_once_with(
        "google-id-token",
        ANY,
        "client-id.apps.googleusercontent.com",
        clock_skew_in_seconds=10,
    )


def test_google_verifier_rejects_failed_verification(monkeypatch) -> None:
    monkeypatch.setattr(settings, "google_client_id", "client-id.apps.googleusercontent.com")
    monkeypatch.setattr(
        "app.modules.user.auth.google.google_id_token.verify_oauth2_token",
        MagicMock(side_effect=ValueError("wrong audience")),
    )

    with pytest.raises(InvalidGoogleTokenError):
        verify_google_id_token("wrong-audience-token")


@pytest.mark.parametrize("missing_claim", ["sub", "email", "name"])
def test_google_verifier_requires_planned_identity_claims(monkeypatch, missing_claim: str) -> None:
    claims = google_identity()
    claims.pop(missing_claim)
    monkeypatch.setattr(settings, "google_client_id", "client-id.apps.googleusercontent.com")
    monkeypatch.setattr(
        "app.modules.user.auth.google.google_id_token.verify_oauth2_token",
        MagicMock(return_value=claims),
    )

    with pytest.raises(InvalidGoogleTokenError):
        verify_google_id_token("missing-claim-token")


def test_google_login_creates_user_and_returns_project_jwt(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.user.routers.auth.verify_google_id_token",
        lambda _: google_identity(),
    )

    response = client.post("/api/auth/google", json={"id_token": "google-id-token"})

    assert response.status_code == 200
    auth = AuthResponse.model_validate(response.json())
    assert auth.is_new_user is True
    assert auth.user == User(
        id=auth.user.id,
        email="student@example.com",
        name="Student Name",
        picture_url="https://example.com/avatar.png",
    )
    assert decode_access_token(auth.access_token) == auth.user.id

    me = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth.access_token}"},
    )
    assert me.status_code == 200
    assert me.json() == auth.user.model_dump()


def test_returning_google_user_preserves_identity_and_profile(client: TestClient, monkeypatch) -> None:
    identity = google_identity()
    monkeypatch.setattr(
        "app.modules.user.routers.auth.verify_google_id_token",
        lambda _: identity,
    )
    first = AuthResponse.model_validate(
        client.post("/api/auth/google", json={"id_token": "first-token"}).json()
    )
    profile = client.put(
        "/api/users/me/profile",
        headers={"Authorization": f"Bearer {first.access_token}"},
        json={
            "display_name": "น้องคอม",
            "age_range": "18_20",
            "user_type": "current_student",
            "study_year": 2,
        },
    )
    assert profile.status_code == 200

    identity.update(
        email="changed@example.com",
        name="Changed Google Name",
        picture="https://example.com/changed.png",
    )
    second_response = client.post("/api/auth/google", json={"id_token": "second-token"})

    assert second_response.status_code == 200
    second = AuthResponse.model_validate(second_response.json())
    assert second.is_new_user is False
    assert second.user.id == first.user.id
    assert second.user.email == "student@example.com"
    assert second.user.name == "Student Name"
    assert second.user.picture_url == "https://example.com/avatar.png"
    assert second.user.display_name == "น้องคอม"
    assert second.user.age_range == "18_20"
    assert second.user.user_type == "current_student"
    assert second.user.study_year == 2
    assert second.user.onboarded is True


def test_google_login_rejects_invalid_token(client: TestClient, monkeypatch) -> None:
    def reject(_: str) -> None:
        raise InvalidGoogleTokenError("invalid")

    monkeypatch.setattr("app.modules.user.routers.auth.verify_google_id_token", reject)

    response = client.post("/api/auth/google", json={"id_token": "invalid-token"})

    assert response.status_code == 401
    assert response.json() == {
        "detail": "ไม่สามารถยืนยันตัวตนด้วย Google ได้ กรุณาลองใหม่"
    }


def test_google_login_reports_missing_client_id_without_breaking_other_auth(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "google_client_id", "")

    google_response = client.post("/api/auth/google", json={"id_token": "any-token"})
    dev_response = client.post(
        "/api/auth/dev",
        json={"email": "dev@example.com", "name": "Dev User"},
    )

    assert google_response.status_code == 503
    assert google_response.json() == {"detail": "ยังไม่ได้ตั้งค่า Google Login"}
    assert dev_response.status_code == 200


def test_google_login_does_not_link_existing_dev_user_by_email(
    client: TestClient,
    monkeypatch,
) -> None:
    dev_response = client.post(
        "/api/auth/dev",
        json={"email": "student@example.com", "name": "Dev User"},
    )
    monkeypatch.setattr(
        "app.modules.user.routers.auth.verify_google_id_token",
        lambda _: google_identity(),
    )

    google_response = client.post("/api/auth/google", json={"id_token": "google-token"})

    assert dev_response.status_code == 200
    assert google_response.status_code == 409
    assert google_response.json() == {"detail": "อีเมลนี้เชื่อมกับบัญชีอื่นอยู่แล้ว"}


def test_profile_update_sets_onboarded_and_preserves_identity(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.user.routers.auth.verify_google_id_token",
        lambda _: google_identity(),
    )
    auth = AuthResponse.model_validate(
        client.post("/api/auth/google", json={"id_token": "google-token"}).json()
    )

    response = client.put(
        "/api/users/me/profile",
        headers={"Authorization": f"Bearer {auth.access_token}"},
        json={
            "display_name": "COPIE Learner",
            "age_range": "21_23",
            "user_type": "prospective",
            "study_year": None,
        },
    )

    assert response.status_code == 200
    user = User.model_validate(response.json())
    assert user.id == auth.user.id
    assert user.email == auth.user.email
    assert user.name == auth.user.name
    assert user.picture_url == auth.user.picture_url
    assert user.display_name == "COPIE Learner"
    assert user.age_range == "21_23"
    assert user.user_type == "prospective"
    assert user.study_year is None
    assert user.onboarded is True


def test_profile_update_requires_authentication(client: TestClient) -> None:
    response = client.put(
        "/api/users/me/profile",
        json={
            "display_name": "Tester",
            "age_range": "21_23",
            "user_type": "prospective",
            "study_year": None,
        },
    )
    assert response.status_code == 401


def query_result(user: UserRow | None) -> MagicMock:
    result = MagicMock()
    result.first.return_value = user
    return result


def test_google_upsert_recovers_from_same_identity_insert_race() -> None:
    concurrent = UserRow(
        google_sub="google-sub-1",
        email="student@example.com",
        name="Concurrent User",
    )
    db = MagicMock(spec=Session)
    db.exec.side_effect = [query_result(None), query_result(None), query_result(concurrent)]
    db.commit.side_effect = IntegrityError("INSERT INTO users", {}, RuntimeError("duplicate"))

    user, is_new_user = upsert_google_user(db, google_identity())

    assert user is concurrent
    assert is_new_user is False
    db.rollback.assert_called_once_with()
    assert db.exec.call_count == 3


def test_google_upsert_reraises_unrelated_integrity_error() -> None:
    db = MagicMock(spec=Session)
    db.exec.side_effect = [
        query_result(None),
        query_result(None),
        query_result(None),
        query_result(None),
    ]
    integrity_error = IntegrityError("INSERT INTO users", {}, RuntimeError("unrelated"))
    db.commit.side_effect = integrity_error

    with pytest.raises(IntegrityError) as exc_info:
        upsert_google_user(db, google_identity())

    assert exc_info.value is integrity_error
    db.rollback.assert_called_once_with()
    assert db.exec.call_count == 4
