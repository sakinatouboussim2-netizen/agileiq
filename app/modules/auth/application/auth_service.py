from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.modules.users.domain.value_objects.enums import Role
from app.modules.users.infrastructure.database.models.user_model import UserModel


def register_user(email: str, password: str, full_name: str) -> UserModel:
    user = UserModel(
        email=email,
        full_name=full_name,
        password_hash=generate_password_hash(password),
        role=Role.MEMBER,
    )

    db.session.add(user)
    db.session.commit()

    return user


def authenticate_user(email: str, password: str) -> dict[str, str]:  # au lieu de -> dict:
    ...
    user = UserModel.query.filter_by(email=email).first()

    if not user:
        raise ValueError("Invalid credentials")

    if not check_password_hash(user.password_hash, password):
        raise ValueError("Invalid credentials")

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value},
    )

    refresh_token = create_refresh_token(
        identity=str(user.id),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
