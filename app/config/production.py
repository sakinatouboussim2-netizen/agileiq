"""Settings durcis pour la production.

Ajoute des validators qui REFUSENT de démarrer si des défauts dangereux
de dev se sont glissés en prod (secrets faibles, CORS ouvert...).
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from app.config.base import BaseAppSettings


class ProductionSettings(BaseAppSettings):
    """Mode production : debug coupé, logs JSON, validations strictes."""

    APP_ENV: Literal["production"] = "production"
    FLASK_DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    @field_validator("SECRET_KEY", "JWT_SECRET_KEY")
    @classmethod
    def _refuse_weak_secrets(cls, value: str) -> str:
        """Empêche un déploiement prod avec un secret de dev ou trop court."""
        if value.startswith("change-me"):
            raise ValueError(
                "Secret de développement détecté en production. "
                "Génère une vraie clé : python -c 'import secrets; print(secrets.token_urlsafe(48))'"
            )
        if len(value) < 32:
            raise ValueError("Les secrets de production doivent faire au moins 32 caractères.")
        return value

    @field_validator("CORS_ORIGINS")
    @classmethod
    def _require_explicit_origins(cls, value: list[str]) -> list[str]:
        """Refuse un CORS_ORIGINS vide ou avec joker en prod."""
        if not value:
            raise ValueError("CORS_ORIGINS doit être défini explicitement en production.")
        if any(o.strip() == "*" for o in value):
            raise ValueError("CORS_ORIGINS=* est interdit en production.")
        return value
