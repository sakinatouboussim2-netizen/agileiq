"""AgileIQ — Flask application factory."""

from __future__ import annotations

import structlog
from flask import Flask

from app.config import Settings, get_settings
from app.extensions import init_extensions
from app.shared.logging import configure_logging
from app.shared.middleware.request_id import init_request_id_middleware


def create_app(settings: Settings | None = None) -> Flask:
    """Construit et configure une instance Flask."""
    settings = settings or get_settings()

    # 1. Logging EN PREMIER : tous les logs ultérieurs en bénéficient
    configure_logging(settings)

    # 2. Application Flask
    app = Flask(__name__)
    app.config.from_mapping(settings.flask_config())

    # 3. Extensions (db, jwt, cors, limiter...)
    init_extensions(app)

    # 4. Middlewares applicatifs
    init_request_id_middleware(app)

    # 5. Blueprints
    _register_blueprints(app)

    # 6. Log de démarrage via structlog (pas plus app.logger.info)
    logger = structlog.get_logger("agileiq")
    logger.info("application.started", env=settings.APP_ENV, log_format=settings.LOG_FORMAT)

    return app


def _register_blueprints(app: Flask) -> None:
    """Enregistre tous les blueprints applicatifs."""
    from app.health import health_bp

    app.register_blueprint(health_bp)
