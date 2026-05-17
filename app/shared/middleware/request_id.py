"""Middleware request_id — corrélation des logs par requête.

À chaque requête HTTP :
  - on lit le header X-Request-ID s'il est fourni (par Nginx ou un client) ;
  - sinon on en génère un (UUID4) ;
  - on le LIE aux contextvars de structlog → présent dans tous les logs
    émis pendant cette requête, sans le passer en argument ;
  - on le renvoie dans la réponse via le header X-Request-ID.
"""

from __future__ import annotations

import uuid

import structlog
from flask import Flask, Response, g, request

REQUEST_ID_HEADER = "X-Request-ID"


def init_request_id_middleware(app: Flask) -> None:
    """Enregistre les hooks before/after request pour le request_id."""

    @app.before_request
    def _set_request_id() -> None:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        g.request_id = request_id
        # Nettoie les contextvars d'une éventuelle requête précédente
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.path,
        )

    @app.after_request
    def _propagate_request_id(response: Response) -> Response:
        request_id = getattr(g, "request_id", None)
        if request_id:
            response.headers[REQUEST_ID_HEADER] = request_id
        return response
