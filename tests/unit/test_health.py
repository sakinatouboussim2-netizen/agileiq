"""Tests unitaires de l'endpoint de santé."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient


@pytest.mark.unit
def test_health_returns_200(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "agileiq-api"}


@pytest.mark.unit
def test_health_response_includes_request_id(client: FlaskClient) -> None:
    response = client.get("/health")
    assert "X-Request-ID" in response.headers


@pytest.mark.unit
def test_health_propagates_custom_request_id(client: FlaskClient) -> None:
    given_id = "test-trace-7"
    response = client.get("/health", headers={"X-Request-ID": given_id})
    assert response.headers["X-Request-ID"] == given_id
