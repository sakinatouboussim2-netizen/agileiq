"""Schémas Marshmallow pour la validation et la sérialisation des projets."""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class ProjectSchema(Schema):
    """Représentation complète d'un projet (utilisée en sortie d'API)."""

    id = fields.UUID(dump_only=True)
    key = fields.Str(required=True, validate=validate.Length(min=2, max=10))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(load_default="")
    owner_id = fields.UUID(required=True)
    is_archived = fields.Bool(load_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProjectCreateSchema(Schema):
    """Payload accepté en entrée pour créer un projet."""

    key = fields.Str(required=True, validate=validate.Length(min=2, max=10))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(load_default="")
    owner_id = fields.UUID(required=True)


class ProjectUpdateSchema(Schema):
    """Payload accepté en entrée pour mettre à jour un projet (partiel)."""

    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str()
    is_archived = fields.Bool()
