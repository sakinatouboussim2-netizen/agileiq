"""Configuration de structlog + bridge avec la stdlib `logging`.

Pourquoi structlog plutôt que `logging.basicConfig` :
- logs structurés (clés/valeurs typées, pas du texte libre) ;
- un seul format en JSON exploitable par Loki/ELK en production ;
- format console lisible et coloré en développement ;
- propagation automatique du `request_id` via contextvars.

Bridge stdlib : Flask et Werkzeug utilisent `logging` standard. On le
configure pour qu'ils passent par le même formateur que structlog —
donc UN SEUL format de logs dans toute l'application.
"""

from __future__ import annotations

import logging
import sys

import structlog
from structlog.types import Processor

from app.config import BaseAppSettings


def configure_logging(settings: BaseAppSettings) -> None:
    """Initialise structlog + logging stdlib. À appeler tôt dans create_app()."""
    log_level = settings.LOG_LEVEL.upper()

    # Processeurs communs : appliqués à TOUS les logs (structlog ET stdlib)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    # Configuration structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Renderer final selon l'environnement
    if settings.LOG_FORMAT == "json":
        final_renderer: Processor = structlog.processors.JSONRenderer()
    else:
        final_renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Formatter qui traite à la fois les logs stdlib (Flask, Werkzeug)
    # et les logs structlog avec les MÊMES processeurs.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            final_renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # Réduit le bruit de bibliothèques bavardes
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
