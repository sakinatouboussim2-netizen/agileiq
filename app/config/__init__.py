"""Configuration multi-environnement — sélection automatique.

Sélectionne la classe de Settings selon la variable d'env APP_ENV :
  - "development"  → DevelopmentSettings
  - "production"   → ProductionSettings
  - "testing"      → TestingSettings

Usage standard :
    from app.config import get_settings
    settings = get_settings()  # singleton mis en cache
"""

from __future__ import annotations

import os
from functools import lru_cache

from app.config.base import BaseAppSettings
from app.config.development import DevelopmentSettings
from app.config.production import ProductionSettings
from app.config.testing import TestingSettings

# Alias pour la rétrocompatibilité avec `from app.config import Settings`
Settings = BaseAppSettings

_SETTINGS_BY_ENV: dict[str, type[BaseAppSettings]] = {
    "development": DevelopmentSettings,
    "production": ProductionSettings,
    "testing": TestingSettings,
}


@lru_cache(maxsize=1)
def get_settings() -> BaseAppSettings:
    """Charge et met en cache l'objet Settings adapté à APP_ENV."""
    env = os.environ.get("APP_ENV", "development").lower()
    settings_cls = _SETTINGS_BY_ENV.get(env)
    if settings_cls is None:
        raise ValueError(
            f"APP_ENV={env!r} inconnu. Valeurs autorisées : {sorted(_SETTINGS_BY_ENV)}"
        )
    return settings_cls()  # type: ignore[call-arg]


__all__ = [
    "BaseAppSettings",
    "DevelopmentSettings",
    "ProductionSettings",
    "Settings",
    "TestingSettings",
    "get_settings",
]
