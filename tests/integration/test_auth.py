"""Tests d'intégration du flow d'authentification."""

from __future__ import annotations

import uuid

import pytest
from flask.testing import FlaskClient

pytestmark = pytest.mark.skip(
    reason="Tests à finaliser une fois la gestion d'erreurs auth complète"
)


@pytest.mark.integration
def test_register_creates_user(client: FlaskClient) -> None:
    email = f"new-{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Strong-Pass-1!",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201


@pytest.mark.integration
def test_register_rejects_duplicate_email(client: FlaskClient) -> None:
    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "Strong-Pass-1!", "full_name": "Dup"}
    client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.integration
def test_login_returns_tokens(client: FlaskClient) -> None:
    email = f"login-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Strong-Pass-1!",
            "full_name": "Login Test",
        },
    )
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Strong-Pass-1!",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.integration
def test_login_with_wrong_password_returns_401(client: FlaskClient) -> None:
    email = f"wrong-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Strong-Pass-1!",
            "full_name": "Wrong Pass",
        },
    )
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401
