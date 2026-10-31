
"""
DisasterMesh - Persistent Alert Model
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def alert_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base):
    __tablename__ = "alerts"

    __table_args__ = (
        Index("ix_alerts_status_severity", "status", "severity"),
        Index("ix_alerts_created_at", "created_at"),
    )

    alert_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    fingerprint: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    source_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="OPEN",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=alert_utc_now,
        nullable=False,
    )

    last_triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=alert_utc_now,
        nullable=False,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    occurrence_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    def __repr__(self) -> str:
        return (
            f"<Alert("
            f"alert_id={self.alert_id}, "
            f"type='{self.alert_type}', "
            f"status='{self.status}'"
            f")>"
        )
