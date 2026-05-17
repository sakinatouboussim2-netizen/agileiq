"""Tests de fumée — l'API se démarre et /health répond correctement."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient


@pytest.mark.unit
def test_health_returns_200_and_expected_payload(client: FlaskClient) -> None:
    """L'endpoint /health doit toujours répondre 200 avec un payload connu."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "agileiq-api"}


@pytest.mark.unit
def test_health_response_includes_request_id_header(client: FlaskClient) -> None:
    """Le middleware request_id doit toujours poser un X-Request-ID en réponse."""
    response = client.get("/health")

    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


@pytest.mark.unit
def test_health_propagates_incoming_request_id(client: FlaskClient) -> None:
    """Si un X-Request-ID est fourni, il doit être conservé dans la réponse."""
    given_id = "test-request-id-12345"
    response = client.get("/health", headers={"X-Request-ID": given_id})

    assert response.headers["X-Request-ID"] == given_id
