"""Settings communs à tous les environnements (parent abstrait).

Contient les champs et la logique partagés. Chaque classe fille
(Development / Production / Testing) surcharge les défauts qui
diffèrent et peut ajouter des validators d'environnement.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """Configuration de base, surchargée par environnement."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Environnement -----------------------------------------------------
    APP_ENV: Literal["development", "testing", "production"] = "development"
    FLASK_DEBUG: bool = False
    TESTING: bool = False

    # --- Secrets (requis) --------------------------------------------------
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRES: int = 900
    JWT_REFRESH_TOKEN_EXPIRES: int = 2_592_000

    # --- Base de données ---------------------------------------------------
    DATABASE_URL: str
    SQLALCHEMY_ECHO: bool = False

    # --- Redis -------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    RATELIMIT_STORAGE_URI: str = "redis://localhost:6379/3"
    RATELIMIT_ENABLED: bool = True

    # --- CORS --------------------------------------------------------------
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    # --- Logs --------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: Any) -> list[str]:
        """Accepte une chaîne CSV ('a,b') ou une vraie liste."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        return []

    def flask_config(self) -> dict[str, Any]:
        """Retourne le sous-ensemble consommé par Flask et ses extensions."""
        return {
            "SECRET_KEY": self.SECRET_KEY,
            "DEBUG": self.FLASK_DEBUG,
            "TESTING": self.TESTING,
            "SQLALCHEMY_DATABASE_URI": self.DATABASE_URL,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ECHO": self.SQLALCHEMY_ECHO,
            "JWT_SECRET_KEY": self.JWT_SECRET_KEY,
            "JWT_ACCESS_TOKEN_EXPIRES": self.JWT_ACCESS_TOKEN_EXPIRES,
            "JWT_REFRESH_TOKEN_EXPIRES": self.JWT_REFRESH_TOKEN_EXPIRES,
            "CORS_ORIGINS": self.CORS_ORIGINS,
            "RATELIMIT_STORAGE_URI": self.RATELIMIT_STORAGE_URI,
            "RATELIMIT_ENABLED": self.RATELIMIT_ENABLED,
        }
