from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

projects_bp = Blueprint(
    "projects",
    __name__,
    url_prefix="/projects",
)


@projects_bp.get("/")
@jwt_required()
def list_projects():
    return jsonify(
        {
            "projects": [],
        }
    )


from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from marshmallow import Schema, fields

projects_bp = Blueprint(
    "projects",
    __name__,
    url_prefix="/projects",
    description="Gestion des projets Agile (CRUD complet)",
)


class ProjectCreateSchema(Schema):
    key = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(allow_none=True)
    owner_id = fields.String(required=True)


class ProjectUpdateSchema(Schema):
    key = fields.String(required=False)
    name = fields.String(required=False)
    description = fields.String(required=False, allow_none=True)


class ProjectSchema(Schema):
    id = fields.String()
    key = fields.String()
    name = fields.String()
    description = fields.String(allow_none=True)
    owner_id = fields.String()
    created_at = fields.String()
    updated_at = fields.String()


@projects_bp.route("/")
class ProjectsCollection(MethodView):
    @jwt_required()
    @projects_bp.response(200, ProjectSchema(many=True))
    def get(self):
        """Liste tous les projets."""
        return []

    @jwt_required()
    @projects_bp.arguments(ProjectCreateSchema)
    @projects_bp.response(201, ProjectSchema)
    def post(self, payload):
        """Crée un nouveau projet."""
        return {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "key": payload["key"],
            "name": payload["name"],
            "description": payload.get("description"),
            "owner_id": payload["owner_id"],
            "created_at": "2026-05-29T09:11:44.510Z",
            "updated_at": "2026-05-29T09:11:44.510Z",
        }


@projects_bp.route("/<project_id>")
class ProjectsItem(MethodView):
    @jwt_required()
    @projects_bp.response(200, ProjectSchema)
    def get(self, project_id):
        """Récupère un projet par son identifiant."""
        return {
            "id": project_id,
            "key": "AGILEIQ",
            "name": "AgileIQ",
            "description": "Projet AgileIQ",
            "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "created_at": "2026-05-29T09:11:44.510Z",
            "updated_at": "2026-05-29T09:11:44.510Z",
        }

    @jwt_required()
    @projects_bp.arguments(ProjectUpdateSchema)
    @projects_bp.response(200, ProjectSchema)
    def patch(self, payload, project_id):
        """Met à jour partiellement un projet."""
        return {
            "id": project_id,
            "key": payload.get("key", "AGILEIQ"),
            "name": payload.get("name", "AgileIQ"),
            "description": payload.get("description", "Projet AgileIQ"),
            "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "created_at": "2026-05-29T09:11:44.510Z",
            "updated_at": "2026-05-29T09:11:44.510Z",
        }

    @jwt_required()
    @projects_bp.response(204)
    def delete(self, project_id):
        """Supprime un projet."""
        return ""
