"""Routes CRUD des projets — documentation OpenAPI auto-générée."""

from __future__ import annotations

from uuid import UUID

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app.extensions import db
from app.modules.projects.infrastructure.database.models.project_model import (
    ProjectModel,
)
from app.modules.projects.presentation.schemas import (
    ProjectCreateSchema,
    ProjectSchema,
    ProjectUpdateSchema,
)

projects_bp = Blueprint(
    "projects",
    "projects",
    url_prefix="/projects",
    description="Gestion des projets Agile (CRUD complet)",
)


@projects_bp.route("/")
class ProjectsCollection(MethodView):
    @jwt_required()
    @projects_bp.response(200, ProjectSchema(many=True))
    def get(self):
        """Liste tous les projets."""
        return db.session.execute(db.select(ProjectModel)).scalars().all()

    @jwt_required()
    @projects_bp.arguments(ProjectCreateSchema)
    @projects_bp.response(201, ProjectSchema)
    def post(self, payload):
        """Crée un nouveau projet."""
        project = ProjectModel(**payload)
        db.session.add(project)
        db.session.commit()
        return project


@projects_bp.route("/<uuid:project_id>")
class ProjectItem(MethodView):
    @jwt_required()
    @projects_bp.response(200, ProjectSchema)
    def get(self, project_id: UUID):
        """Récupère un projet par son identifiant."""
        project = db.session.get(ProjectModel, project_id)
        if project is None:
            abort(404, message="Projet introuvable.")
        return project

    @jwt_required()
    @projects_bp.arguments(ProjectUpdateSchema)
    @projects_bp.response(200, ProjectSchema)
    def patch(self, payload, project_id: UUID):
        """Met à jour partiellement un projet."""
        project = db.session.get(ProjectModel, project_id)
        if project is None:
            abort(404, message="Projet introuvable.")
        for key, value in payload.items():
            setattr(project, key, value)
        db.session.commit()
        return project

    @jwt_required()
    @projects_bp.response(204)
    def delete(self, project_id: UUID):
        """Supprime un projet."""
        project = db.session.get(ProjectModel, project_id)
        if project is None:
            abort(404, message="Projet introuvable.")
        db.session.delete(project)
        db.session.commit()
        return ""
