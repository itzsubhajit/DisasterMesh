
"""
DisasterMesh Backend - Database Models

Six core entities:
Users, Nodes, Messages, Routes, EmergencyRequests, Logs.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# =========================================================
# USERS
# =========================================================

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    token_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<User("
            f"user_id={self.user_id}, "
            f"username='{self.username}', "
            f"role='{self.role}', "
            f"is_active={self.is_active}"
            f")>"
        )


# =========================================================
# NODES
# =========================================================

class Node(Base):
    __tablename__ = "nodes"

    node_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    device_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    node_type: Mapped[str] = mapped_column(
        String(30),
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

    battery_level: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender_node",
    )

    source_routes: Mapped[list["Route"]] = relationship(
        "Route",
        foreign_keys="Route.source",
        back_populates="source_node",
    )

    destination_routes: Mapped[list["Route"]] = relationship(
        "Route",
        foreign_keys="Route.destination",
        back_populates="destination_node",
    )

    next_hop_routes: Mapped[list["Route"]] = relationship(
        "Route",
        foreign_keys="Route.next_hop",
        back_populates="next_hop_node",
    )

    logs: Mapped[list["Log"]] = relationship(
        "Log",
        back_populates="node",
    )

    def __repr__(self) -> str:
        return (
            f"<Node("
            f"node_id='{self.node_id}', "
            f"device_id='{self.device_id}', "
            f"status='{self.status}'"
            f")>"
        )


# =========================================================
# MESSAGES
# =========================================================

class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
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

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
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

    # AI outputs are recommendations only. The original category and priority
    # above remain unchanged and continue to represent the received packet.
    ai_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_category_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_category_probabilities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    ai_priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ai_priority_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_priority_probabilities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    ai_requires_human_review: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    ai_review_reasons: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ai_matched_high_risk_phrases: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ai_decision_authority: Mapped[str] = mapped_column(
        String(30), nullable=False, default="HUMAN_OPERATOR", server_default="HUMAN_OPERATOR"
    )
    ai_model_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    sender_node: Mapped["Node"] = relationship(
        "Node",
        foreign_keys=[sender_id],
        back_populates="messages",
    )

    receiver_node: Mapped[Optional["Node"]] = relationship(
        "Node",
        foreign_keys=[receiver_id],
    )

    emergency_request: Mapped[Optional["EmergencyRequest"]] = relationship(
        "EmergencyRequest",
        back_populates="message",
        uselist=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Message("
            f"message_id='{self.message_id}', "
            f"sender_id='{self.sender_id}', "
            f"priority='{self.priority}', "
            f"status='{self.status}'"
            f")>"
        )


# =========================================================
# ROUTES
# =========================================================

class Route(Base):
    __tablename__ = "routes"

    route_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source: Mapped[str] = mapped_column(
        ForeignKey("nodes.node_id"),
        nullable=False,
        index=True,
    )

    destination: Mapped[str] = mapped_column(
        ForeignKey("nodes.node_id"),
        nullable=False,
        index=True,
    )

    next_hop: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nodes.node_id"),
        nullable=True,
        index=True,
    )

    hop_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    quality: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    source_node: Mapped["Node"] = relationship(
        "Node",
        foreign_keys=[source],
        back_populates="source_routes",
    )

    destination_node: Mapped["Node"] = relationship(
        "Node",
        foreign_keys=[destination],
        back_populates="destination_routes",
    )

    next_hop_node: Mapped[Optional["Node"]] = relationship(
        "Node",
        foreign_keys=[next_hop],
        back_populates="next_hop_routes",
    )

    def __repr__(self) -> str:
        return (
            f"<Route("
            f"route_id={self.route_id}, "
            f"source='{self.source}', "
            f"destination='{self.destination}', "
            f"next_hop='{self.next_hop}', "
            f"status='{self.status}'"
            f")>"
        )


# =========================================================
# EMERGENCY REQUESTS
# =========================================================

class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    request_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.message_id"),
        unique=True,
        nullable=False,
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

    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="NEW",
    )

    assigned_team: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    assigned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Explicit, auditable operator review of the AI recommendation.
    ai_reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ai_reviewed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.user_id"), nullable=True
    )
    ai_review_decision: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    ai_review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    message: Mapped["Message"] = relationship(
        "Message",
        back_populates="emergency_request",
    )

    @property
    def ai_category(self) -> Optional[str]:
        return self.message.ai_category if self.message is not None else None

    @property
    def ai_category_confidence(self) -> Optional[float]:
        return (
            self.message.ai_category_confidence
            if self.message is not None else None
        )

    @property
    def ai_priority(self) -> Optional[str]:
        return self.message.ai_priority if self.message is not None else None

    @property
    def ai_priority_confidence(self) -> Optional[float]:
        return (
            self.message.ai_priority_confidence
            if self.message is not None else None
        )

    @property
    def ai_requires_human_review(self) -> bool:
        return bool(
            self.message is not None
            and self.message.ai_requires_human_review
        )

    @property
    def ai_review_reasons(self) -> Optional[list]:
        return self.message.ai_review_reasons if self.message is not None else None

    def __repr__(self) -> str:
        return (
            f"<EmergencyRequest("
            f"request_id={self.request_id}, "
            f"message_id='{self.message_id}', "
            f"status='{self.status}'"
            f")>"
        )


# =========================================================
# LOGS
# =========================================================

class Log(Base):
    __tablename__ = "logs"

    log_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    node_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nodes.node_id"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    node: Mapped[Optional["Node"]] = relationship(
        "Node",
        back_populates="logs",
    )

    def __repr__(self) -> str:
        return (
            f"<Log("
            f"log_id={self.log_id}, "
            f"event_type='{self.event_type}', "
            f"node_id='{self.node_id}'"
            f")>"
        )
