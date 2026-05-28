from datetime import UTC, datetime

from sqlalchemy.orm import Mapped, mapped_column


class TimestampedModel:
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
