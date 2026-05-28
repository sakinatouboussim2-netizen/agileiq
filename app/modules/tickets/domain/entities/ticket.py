from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.modules.tickets.domain.value_objects.enums import Severity, TicketType


@dataclass
class Ticket:
    type: TicketType
    title: str
    project_id: UUID
    reporter_id: UUID
    severity: Severity | None = None
    parent_id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Le titre est obligatoire.")

        if self.severity and self.type is not TicketType.BUG:
            raise ValueError("La sévérité n'est applicable qu'aux bugs.")

        if self.type is TicketType.EPIC and self.parent_id:
            raise ValueError("Un epic ne peut pas avoir de parent.")
