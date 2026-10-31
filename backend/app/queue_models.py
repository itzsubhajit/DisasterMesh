
"""
DisasterMesh - Persistent Packet Queue Model

Stores packets waiting for synchronization with the main
DisasterMesh message database.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from .models import Node as _Node  # Register nodes table and its foreign keys.


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PacketQueue(Base):
    __tablename__ = "packet_queue"

    __table_args__ = (
        Index("ix_packet_queue_status_next_retry", "status", "next_retry_at"),
    )

    queue_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    message_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    sender_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.node_id"),
        nullable=False,
        index=True,
    )

    receiver_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nodes.node_id"),
        nullable=True,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    ttl: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    hop_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="QUEUED",
        index=True,
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    next_retry_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<PacketQueue("
            f"queue_id={self.queue_id}, "
            f"message_id='{self.message_id}', "
            f"status='{self.status}'"
            f")>"
        )
