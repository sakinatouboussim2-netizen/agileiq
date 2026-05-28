from flask import Blueprint, jsonify, request

from app.modules.auth.application.auth_service import (
    authenticate_user,
    register_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    payload = request.get_json()

    register_user(
        email=payload["email"],
        password=payload["password"],
        full_name=payload["full_name"],
    )

    return (
        jsonify(
            {
                "message": "User registered successfully",
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    payload = request.get_json()

    tokens = authenticate_user(
        email=payload["email"],
        password=payload["password"],
    )

    return jsonify(tokens), 200
