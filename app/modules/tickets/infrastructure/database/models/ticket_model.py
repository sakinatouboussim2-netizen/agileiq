from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.modules.tickets.domain.value_objects.enums import Severity, TicketType
from app.shared.database.base import TimestampedModel


class TicketModel(db.Model, TimestampedModel):  # type: ignore[name-defined]
    __tablename__ = "tickets"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    type: Mapped[TicketType] = mapped_column(
        Enum(TicketType),
        nullable=False,
    )

    severity: Mapped[Severity | None] = mapped_column(
        Enum(Severity),
        nullable=True,
    )

    project_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    reporter_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tickets.id"),
        nullable=True,
    )
