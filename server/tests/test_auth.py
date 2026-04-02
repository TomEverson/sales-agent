"""Tests for TB-36: Admin Authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from routers.auth import ensure_admin_user


@pytest.fixture(autouse=True)
def seed_admin(setup_database):
    """Ensure admin user exists before each test."""
    from tests.conftest import test_engine

    with Session(test_engine) as session:
        ensure_admin_user(session)


class TestLogin:
    def test_login_success(self, client: TestClient):
        resp = client.post(
            "/auth/login", json={"email": "admin@gmail.com", "password": "admin123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient):
        resp = client.post(
            "/auth/login", json={"email": "admin@gmail.com", "password": "wrong"}
        )
        assert resp.status_code == 401

    def test_login_unknown_email(self, client: TestClient):
        resp = client.post(
            "/auth/login", json={"email": "unknown@example.com", "password": "admin123"}
        )
        assert resp.status_code == 401


class TestVerify:
    def test_verify_valid_token(self, client: TestClient):
        login_resp = client.post(
            "/auth/login", json={"email": "admin@gmail.com", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]
        resp = client.get("/auth/verify", params={"token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@gmail.com"
        assert data["is_admin"] is True

    def test_verify_invalid_token(self, client: TestClient):
        resp = client.get("/auth/verify", params={"token": "not-a-valid-token"})
        assert resp.status_code == 401

    def test_verify_tampered_token(self, client: TestClient):
        resp = client.get(
            "/auth/verify", params={"token": "eyJhbGciOiJIUzI1NiJ9.tampered.signature"}
        )
        assert resp.status_code == 401
