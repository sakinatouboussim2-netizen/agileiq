"""AgileIQ — Flask application factory.

Le pattern *application factory* (`create_app`) est la norme en Flask :
- aucune instance globale d'`app` n'est créée à l'import du module ;
- chaque appel produit une instance indépendante, paramétrable ;
- les tests peuvent instancier une app dédiée par cas de test.

Point d'entrée Gunicorn et Flask CLI : `app.wsgi:app`.
"""

from __future__ import annotations

from flask import Flask

from app.config import Settings, get_settings
from app.extensions import init_extensions


def create_app(settings: Settings | None = None) -> Flask:
    """Construit et configure une instance Flask."""
    app = Flask(__name__)

    settings = settings or get_settings()
    app.config.from_mapping(settings.flask_config())

    init_extensions(app)
    _register_blueprints(app)

    app.logger.info("AgileIQ application created (env=%s)", settings.APP_ENV)
    return app


def _register_blueprints(app: Flask) -> None:
    """Enregistre tous les blueprints applicatifs."""
    from app.health import health_bp

    app.register_blueprint(health_bp)
