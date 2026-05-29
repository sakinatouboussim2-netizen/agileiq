"""Schémas Marshmallow pour la validation et la sérialisation des tickets."""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class TicketSchema(Schema):
    id = fields.UUID(dump_only=True)
    type = fields.Str(required=True, validate=validate.OneOf(["epic", "feature", "bug"]))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    severity = fields.Str(
        validate=validate.OneOf(["trivial", "minor", "major", "critical", "blocker"]),
        allow_none=True,
    )
    project_id = fields.UUID(required=True)
    reporter_id = fields.UUID(required=True)
    parent_id = fields.UUID(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TicketCreateSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(["epic", "feature", "bug"]))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    severity = fields.Str(
        validate=validate.OneOf(["trivial", "minor", "major", "critical", "blocker"]),
        allow_none=True,
    )
    project_id = fields.UUID(required=True)
    reporter_id = fields.UUID(required=True)
    parent_id = fields.UUID(allow_none=True)
