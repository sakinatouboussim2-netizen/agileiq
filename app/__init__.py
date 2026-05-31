"""AgileIQ — Flask application factory."""

from __future__ import annotations

import structlog
from flask import Flask

from app.config import Settings, get_settings
from app.extensions import init_extensions
from app.shared.logging import configure_logging
from app.shared.middleware.request_id import init_request_id_middleware


def _import_models() -> None:
    from app.modules.projects.infrastructure.database.models import project_model
    from app.modules.tickets.infrastructure.database.models import ticket_model
    from app.modules.users.infrastructure.database.models import user_model


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
    _import_models()

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

    from app.extensions import api
    from app.health import health_bp
    from app.modules.auth.presentation.auth_routes import auth_bp
    from app.modules.projects.presentation.project_routes import projects_bp
    from app.modules.tickets.presentation.ticket_routes import tickets_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)

    api.register_blueprint(projects_bp)
    api.register_blueprint(tickets_bp)
