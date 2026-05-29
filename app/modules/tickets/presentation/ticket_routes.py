"""Routes CRUD des tickets — documentation OpenAPI auto-générée."""

from __future__ import annotations

from uuid import UUID

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.modules.tickets.infrastructure.database.models.ticket_model import (
    TicketModel,
)
from app.modules.tickets.presentation.schemas import (
    TicketCreateSchema,
    TicketSchema,
)

tickets_bp = Blueprint(
    "tickets",
    "tickets",
    url_prefix="/tickets",
    description="Gestion des tickets (epics, features, bugs)",
)


@tickets_bp.route("/")
class TicketsCollection(MethodView):
    @jwt_required()
    @tickets_bp.response(200, TicketSchema(many=True))
    def get(self):
        """Liste tous les tickets."""
        return db.session.execute(db.select(TicketModel)).scalars().all()

    @jwt_required()
    @tickets_bp.arguments(TicketCreateSchema)
    @tickets_bp.response(201, TicketSchema)
    def post(self, payload):
        """Crée un nouveau ticket."""
        ticket = TicketModel(**payload)
        db.session.add(ticket)
        db.session.commit()
        return ticket


@tickets_bp.route("/<uuid:ticket_id>")
class TicketItem(MethodView):
    @jwt_required()
    @tickets_bp.response(200, TicketSchema)
    def get(self, ticket_id: UUID):
        """Récupère un ticket par son identifiant."""
        ticket = db.session.get(TicketModel, ticket_id)
        if ticket is None:
            abort(404, message="Ticket introuvable.")
        return ticket
