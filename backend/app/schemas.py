from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


# =========================================================
# Base Schema
# =========================================================

class DisasterMeshSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("*", when_used="json")
    def serialize_datetime_values_as_utc(self, value):
        """Serialize naive SQLite datetimes as UTC and include an explicit Z.

        SQLAlchemy's SQLite DateTime columns do not preserve tzinfo even when
        the Python value was created as timezone-aware UTC. DisasterMesh stores
        these timestamps in UTC, so a naive value read from SQLite is treated
        as UTC rather than as the browser/operator's local timezone.
        """
        if not isinstance(value, datetime):
            return value

        if value.tzinfo is None or value.utcoffset() is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        return value.isoformat().replace("+00:00", "Z")


# =========================================================
# Authentication
# =========================================================

class LoginRequest(DisasterMeshSchema):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=255)


class LoginResponse(DisasterMeshSchema):
    access_token: str
    token_type: str = "bearer"
    username: str
    name: str
    role: str


# =========================================================
# User Schemas
# =========================================================

class UserResponse(DisasterMeshSchema):
    user_id: int
    name: str
    role: str
    username: str
    created_at: datetime


# =========================================================
# Node Schemas
# =========================================================

class NodeCreate(DisasterMeshSchema):
    node_id: str = Field(min_length=2, max_length=50)
    device_id: str = Field(min_length=2, max_length=100)
    node_type: str = Field(default="FIELD", max_length=30)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    battery_level: Optional[float] = Field(default=None, ge=0, le=100)
    status: str = Field(default="ONLINE", max_length=30)


class NodeHeartbeat(DisasterMeshSchema):
    battery_level: Optional[float] = Field(default=None, ge=0, le=100)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class NodeResponse(DisasterMeshSchema):
    node_id: str
    device_id: str
    node_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery_level: Optional[float] = None
    status: str
    last_seen: Optional[datetime] = None


class NodeStatusResponse(DisasterMeshSchema):
    total_nodes: int
    online_nodes: int
    offline_nodes: int
    stale_nodes: int


# =========================================================
# Message Schemas
# =========================================================

class MessageCreate(DisasterMeshSchema):
    message_id: str = Field(min_length=1, max_length=100)
    sender_id: str = Field(min_length=2, max_length=50)
    receiver_id: Optional[str] = Field(default=None, max_length=50)
    category: str = Field(min_length=1, max_length=50)
    priority: str = Field(default="MEDIUM", max_length=20)
    content: str = Field(min_length=1, max_length=2000)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    ttl: int = Field(default=5, ge=1, le=255)
    hop_count: int = Field(default=0, ge=0)


class MessageResponse(DisasterMeshSchema):
    message_id: str
    sender_id: str
    receiver_id: Optional[str] = None
    category: str
    priority: str
    content: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: datetime
    status: str
    ttl: int
    hop_count: int

    # AI fields are separate recommendations; they do not overwrite the
    # category and priority received in the original message.
    ai_category: Optional[str] = None
    ai_category_confidence: Optional[float] = None
    ai_category_probabilities: Optional[dict] = None
    ai_priority: Optional[str] = None
    ai_priority_confidence: Optional[float] = None
    ai_priority_probabilities: Optional[dict] = None
    ai_requires_human_review: bool = False
    ai_review_reasons: Optional[list[str]] = None
    ai_matched_high_risk_phrases: Optional[list[str]] = None
    ai_decision_authority: str = "HUMAN_OPERATOR"
    ai_model_info: Optional[dict] = None


# =========================================================
# Emergency Request Schemas
# =========================================================

class EmergencyCreate(DisasterMeshSchema):
    message_id: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    priority: str = Field(default="MEDIUM", max_length=20)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    status: str = Field(default="NEW", max_length=30)
    assigned_team: Optional[str] = Field(default=None, max_length=120)


class EmergencyResponse(DisasterMeshSchema):
    request_id: int
    message_id: str
    category: str
    priority: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    assigned_team: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    ai_category: Optional[str] = None
    ai_category_confidence: Optional[float] = None
    ai_priority: Optional[str] = None
    ai_priority_confidence: Optional[float] = None
    ai_requires_human_review: bool = False
    ai_review_reasons: Optional[list[str]] = None

    ai_reviewed_at: Optional[datetime] = None
    ai_reviewed_by: Optional[int] = None
    ai_review_decision: Optional[str] = None
    ai_review_notes: Optional[str] = None


class EmergencyStatusUpdate(DisasterMeshSchema):
    status: str = Field(min_length=1, max_length=30)
    assigned_team: Optional[str] = Field(default=None, max_length=120)


class EmergencyAIReview(DisasterMeshSchema):
    decision: Literal["CONFIRM_AI", "OVERRIDE"]
    final_category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    final_priority: Optional[Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


# =========================================================
# Route Schemas
# =========================================================

class RouteCreate(DisasterMeshSchema):
    source: str = Field(min_length=2, max_length=50)
    destination: str = Field(min_length=2, max_length=50)
    next_hop: Optional[str] = Field(default=None, max_length=50)
    hop_count: int = Field(default=0, ge=0)
    quality: Optional[float] = Field(default=None, ge=0, le=100)
    status: str = Field(default="ACTIVE", max_length=30)


class RouteResponse(DisasterMeshSchema):
    route_id: int
    source: str
    destination: str
    next_hop: Optional[str] = None
    hop_count: int
    quality: Optional[float] = None
    status: str
    updated_at: datetime


# =========================================================
# Log Schemas
# =========================================================

class LogCreate(DisasterMeshSchema):
    node_id: Optional[str] = Field(default=None, max_length=50)
    event_type: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=2000)


class LogResponse(DisasterMeshSchema):
    log_id: int
    node_id: Optional[str] = None
    event_type: str
    description: str
    timestamp: datetime


# =========================================================
# Packet Queue Schemas
# =========================================================

class PacketQueueCreate(DisasterMeshSchema):
    message_id: str = Field(min_length=1, max_length=100)
    sender_id: str = Field(min_length=2, max_length=50)
    receiver_id: Optional[str] = Field(default=None, max_length=50)

    category: str = Field(min_length=1, max_length=50)
    priority: str = Field(default="MEDIUM", max_length=20)
    content: str = Field(min_length=1, max_length=2000)

    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    ttl: int = Field(default=5, ge=1, le=255)
    hop_count: int = Field(default=0, ge=0)

    retention_minutes: int = Field(default=1440, ge=1, le=10080)
    max_attempts: int = Field(default=5, ge=1, le=20)


class PacketQueueResponse(DisasterMeshSchema):
    queue_id: int
    message_id: str
    sender_id: str
    receiver_id: Optional[str] = None

    category: str
    priority: str
    content: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    ttl: int
    hop_count: int

    status: str
    attempt_count: int
    max_attempts: int

    queued_at: datetime
    last_attempt_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    synced_at: Optional[datetime] = None

    last_error: Optional[str] = None


class PacketQueueStatsResponse(DisasterMeshSchema):
    total_items: int
    queued_items: int
    syncing_items: int
    synced_items: int
    failed_items: int
    expired_items: int


class PacketQueueProcessResponse(DisasterMeshSchema):
    checked: int
    synced: int
    retry_scheduled: int
    failed: int
    expired: int


# =========================================================
# System Status
# =========================================================

class SystemStatusResponse(DisasterMeshSchema):
    system: str
    backend: str
    database: str
    status: str