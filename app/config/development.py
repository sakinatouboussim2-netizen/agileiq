"""Settings optimisés pour le développement local."""

from __future__ import annotations

from typing import Literal

from app.config.base import BaseAppSettings


class DevelopmentSettings(BaseAppSettings):
    """Mode développement : debug activé, logs lisibles, faible rigueur."""

    APP_ENV: Literal["development"] = "development"
    FLASK_DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = False  # passe à True pour tracer les requêtes SQL
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: Literal["json", "console"] = "console"
