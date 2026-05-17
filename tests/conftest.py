"""Fixtures pytest partagées.

Une fixture `app` construit une Flask app avec TestingSettings.
Une fixture `client` expose le client HTTP de test (pas de réseau réel).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import TestingSettings


@pytest.fixture
def app() -> Iterator[Flask]:
    """Instance Flask configurée pour les tests."""
    settings = TestingSettings()
    flask_app = create_app(settings=settings)
    yield flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Client HTTP de test (Werkzeug, in-memory, sans réseau)."""
    return app.test_client()
