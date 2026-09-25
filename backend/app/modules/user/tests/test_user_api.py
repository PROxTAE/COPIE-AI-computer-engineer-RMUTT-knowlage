"""Contract-level tests for the Phase 1 user API."""

from collections.abc import Generator

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.modules.user.auth.jwt import create_access_token, decode_access_token
from app.modules.user.database import get_session
from app.modules.user.routers import router


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
    monkeypatch.setattr(settings, "jwt_secret", "test-only-secret-that-is-at-least-32-bytes")
    monkeypatch.setattr(settings, "dev_auth", True)
    with TestClient(app) as test_client:
        yield test_client


def dev_login(client: TestClient) -> dict:
    response = client.post(
        "/api/auth/dev",
        json={"email": "Tester@Example.com", "name": "Tester"},
    )
    assert response.status_code == 200
    return response.json()


def test_dev_login_returns_contract_and_reuses_user(client: TestClient) -> None:
    first = dev_login(client)
    assert first["is_new_user"] is True
    assert first["user"] == {
        "id": first["user"]["id"],
        "email": "tester@example.com",
        "name": "Tester",
        "picture_url": None,
        "display_name": None,
        "age_range": None,
        "user_type": None,
        "study_year": None,
        "onboarded": False,
    }
    assert decode_access_token(first["access_token"]) == first["user"]["id"]

    second = dev_login(client)
    assert second["is_new_user"] is False
    assert second["user"]["id"] == first["user"]["id"]


def test_dev_login_is_hidden_when_disabled(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(settings, "dev_auth", False)
    response = client.post(
        "/api/auth/dev",
        json={"email": "tester@example.com", "name": "Tester"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "ไม่พบ endpoint นี้"}


def test_users_me_accepts_issued_token(client: TestClient) -> None:
    login = dev_login(client)
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json() == login["user"]


def test_users_me_rejects_missing_token_with_thai_detail(client: TestClient) -> None:
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "ไม่สามารถยืนยันตัวตนได้ กรุณาเข้าสู่ระบบใหม่"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_users_me_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer not-a-token"},
    )
    assert response.status_code == 401


def test_users_me_rejects_token_for_missing_user(client: TestClient) -> None:
    token = create_access_token("missing-user")
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_decode_rejects_token_signed_with_another_secret(client: TestClient) -> None:
    token = jwt.encode({"sub": "user-id"}, "wrong-secret-that-is-at-least-32-bytes", algorithm="HS256")
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_main_app_mounts_user_endpoints() -> None:
    from app.main import app

    paths = set(app.openapi()["paths"])
    assert {"/api/auth/dev", "/api/users/me"} <= paths
