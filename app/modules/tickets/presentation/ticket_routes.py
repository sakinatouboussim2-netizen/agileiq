from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from marshmallow import Schema, fields

tickets_bp = Blueprint(
    "tickets",
    __name__,
    url_prefix="/tickets",
    description="Gestion des tickets (epics, features, bugs)",
)


class TicketCreateSchema(Schema):
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    type = fields.String(required=True)
    severity = fields.String(allow_none=True)
    project_id = fields.String(required=True)
    reporter_id = fields.String(required=True)
    parent_id = fields.String(allow_none=True)


class TicketSchema(Schema):
    id = fields.String()
    title = fields.String()
    description = fields.String(allow_none=True)
    type = fields.String()
    severity = fields.String(allow_none=True)
    project_id = fields.String()
    reporter_id = fields.String()
    parent_id = fields.String(allow_none=True)
    created_at = fields.String()
    updated_at = fields.String()


@tickets_bp.route("/")
class TicketsCollection(MethodView):
    @jwt_required()
    @tickets_bp.response(200, TicketSchema(many=True))
    def get(self):
        """Liste tous les tickets."""
        return []

    @jwt_required()
    @tickets_bp.arguments(TicketCreateSchema)
    @tickets_bp.response(201, TicketSchema)
    def post(self, payload):
        """Crée un nouveau ticket."""
        return {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": payload["title"],
            "description": payload.get("description"),
            "type": payload["type"],
            "severity": payload.get("severity"),
            "project_id": payload["project_id"],
            "reporter_id": payload["reporter_id"],
            "parent_id": payload.get("parent_id"),
            "created_at": "2026-05-29T09:11:44.510Z",
            "updated_at": "2026-05-29T09:11:44.510Z",
        }


@tickets_bp.route("/<ticket_id>")
class TicketsItem(MethodView):
    @jwt_required()
    @tickets_bp.response(200, TicketSchema)
    def get(self, ticket_id):
        """Récupère un ticket par son identifiant."""
        return {
            "id": ticket_id,
            "title": "Crash au login",
            "description": "Erreur 500 sur Firefox",
            "type": "bug",
            "severity": "major",
            "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "reporter_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "parent_id": None,
            "created_at": "2026-05-29T09:11:44.510Z",
            "updated_at": "2026-05-29T09:11:44.510Z",
        }
