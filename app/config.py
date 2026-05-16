"""Configuration applicative typée (Pydantic Settings).

Source de vérité unique pour TOUTE la configuration de l'application.
Charge depuis :
  1. les variables d'environnement (priorité haute, utilisé en prod) ;
  2. le fichier `.env` à la racine (fallback dev local).

NOTE : version simple pour la sous-étape 0.4. Sera refactorisée en
package `app/config/` multi-environnement en sous-étape 0.5.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application, typée et validée au démarrage."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: Literal["development", "testing", "production"] = "development"
    FLASK_DEBUG: bool = False

    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRES: int = 900
    JWT_REFRESH_TOKEN_EXPIRES: int = 2_592_000

    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    RATELIMIT_STORAGE_URI: str = "redis://localhost:6379/3"

    CORS_ORIGINS: list[str] = Field(default_factory=list)

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        return []

    def flask_config(self) -> dict[str, Any]:
        """Retourne uniquement le sous-ensemble consommé par Flask et ses extensions."""
        return {
            "SECRET_KEY": self.SECRET_KEY,
            "DEBUG": self.FLASK_DEBUG,
            "SQLALCHEMY_DATABASE_URI": self.DATABASE_URL,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JWT_SECRET_KEY": self.JWT_SECRET_KEY,
            "JWT_ACCESS_TOKEN_EXPIRES": self.JWT_ACCESS_TOKEN_EXPIRES,
            "JWT_REFRESH_TOKEN_EXPIRES": self.JWT_REFRESH_TOKEN_EXPIRES,
            "CORS_ORIGINS": self.CORS_ORIGINS,
            "RATELIMIT_STORAGE_URI": self.RATELIMIT_STORAGE_URI,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton mis en cache : Settings est parsé une seule fois au démarrage."""
    return Settings()  # type: ignore[call-arg]
