"""Endpoint de health check.

Expose /health pour les sondes de liveness Docker / Kubernetes / Nginx.
Cette version (Phase 0) renvoie 200 dès que le process Flask répond.
"""

from __future__ import annotations

from flask import Blueprint, Response, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health() -> tuple[Response, int]:
    """Liveness probe — vérifie uniquement que le process répond."""
    return jsonify(status="ok", service="agileiq-api"), 200
