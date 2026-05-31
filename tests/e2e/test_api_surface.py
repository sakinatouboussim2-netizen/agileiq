"""Tests end-to-end de la surface API publique."""

from __future__ import annotations

import uuid

import pytest
from flask.testing import FlaskClient

pytestmark = pytest.mark.skip(
    reason="Tests e2e à finaliser une fois le client de test smorest configuré"
)


@pytest.mark.e2e
def test_create_project_requires_authentication(client: FlaskClient) -> None:
    response = client.post(
        "/projects/",
        json={
            "key": "DEMO",
            "name": "Test",
            "owner_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 401


@pytest.mark.e2e
def test_list_projects_requires_authentication(client: FlaskClient) -> None:
    response = client.get("/projects/")
    assert response.status_code == 401


@pytest.mark.e2e
def test_swagger_ui_is_accessible(client: FlaskClient) -> None:
    """Swagger UI doit être disponible sur /docs sans authentification."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"AgileIQ API" in response.data


@pytest.mark.e2e
def test_openapi_spec_is_served(client: FlaskClient) -> None:
    """Le fichier openapi.json doit être généré automatiquement."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.get_json()
    assert spec["info"]["title"] == "AgileIQ API"
    assert "/projects/" in spec["paths"]
    assert "/tickets/" in spec["paths"]
