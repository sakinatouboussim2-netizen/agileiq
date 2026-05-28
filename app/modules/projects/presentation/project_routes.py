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
