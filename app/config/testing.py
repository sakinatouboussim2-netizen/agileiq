"""Settings pour les tests automatisés.

Valeurs par défaut suffisantes pour faire tourner pytest sans variables
d'env. Les tests d'intégration peuvent surcharger DATABASE_URL via env.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import field_validator

from app.config.base import BaseAppSettings


class TestingSettings(BaseAppSettings):
    """Mode test : secrets bidons, rate limiting off, JWT courts."""

    APP_ENV: Literal["testing"] = "testing"
    TESTING: bool = True
    FLASK_DEBUG: bool = False

    # Secrets factices : suffisants pour les tests, JAMAIS pour autre chose
    SECRET_KEY: str = "test-secret-key-do-not-use-outside-tests"
    JWT_SECRET_KEY: str = "test-jwt-secret-do-not-use-outside-tests"

    # Base de test (à surcharger pour les tests d'intégration vrais)
    DATABASE_URL: str = "postgresql+psycopg://test:test@localhost:5432/agileiq_test"

    # Désactive rate limiting et logs verbeux (sinon les tests sont bruyants)
    RATELIMIT_ENABLED: bool = False
    LOG_LEVEL: str = "WARNING"

    # Tokens très courts pour tester l'expiration sans attendre
    JWT_ACCESS_TOKEN_EXPIRES: int = 5
    JWT_REFRESH_TOKEN_EXPIRES: int = 60

    @field_validator("APP_ENV", mode="before")
    @classmethod
    def _force_testing(cls, _value: Any) -> str:
        """Force APP_ENV='testing' quelle que soit la variable d'env.

        Sans ce validator, exécuter pytest dans un conteneur Docker qui a
        APP_ENV=development (cas du dev) ferait échouer la validation du
        Literal['testing'].
        """
        return "testing"
