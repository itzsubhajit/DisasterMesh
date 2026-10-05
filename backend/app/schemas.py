from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# Base Schema
# =========================================================

class DisasterMeshSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# Authentication
# =========================================================

class LoginRequest(DisasterMeshSchema):
    username: str = Field(
        min_length=1,
        max_length=80
    )
    password: str = Field(
        min_length=1,
        max_length=255
    )


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
    node_id: str = Field(
        min_length=2,
        max_length=50
    )

    device_id: str = Field(
        min_length=2,
        max_length=100
    )

    node_type: str = Field(
        default="FIELD",
        max_length=30
    )

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    battery_level: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    status: str = Field(
        default="ONLINE",
        max_length=30
    )

class NodeResponse(DisasterMeshSchema):
    node_id: str
    device_id: str
    node_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery_level: Optional[float] = None
    status: str
    last_seen: Optional[datetime] = None


# =========================================================
# Message Schemas
# =========================================================

class MessageCreate(DisasterMeshSchema):
    message_id: str = Field(
        min_length=1,
        max_length=100
    )

    sender_id: Optional[int] = None

    receiver_id: Optional[int] = None

    category: str = Field(
        min_length=1,
        max_length=50
    )

    priority: str = Field(
        default="MEDIUM",
        max_length=20
    )

    content: str = Field(
        min_length=1,
        max_length=2000
    )

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    ttl: int = Field(
        default=5,
        ge=0,
        le=255
    )

    hop_count: int = Field(
        default=0,
        ge=0
    )


class MessageResponse(DisasterMeshSchema):
    message_id: str
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    category: str
    priority: str
    content: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: datetime
    status: str
    ttl: int
    hop_count: int


# =========================================================
# Emergency Request Schemas
# =========================================================

class EmergencyCreate(DisasterMeshSchema):
    message_id: str = Field(
        min_length=1,
        max_length=100
    )

    category: str = Field(
        min_length=1,
        max_length=50
    )

    priority: str = Field(
        default="MEDIUM",
        max_length=20
    )

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    status: str = Field(
        default="NEW",
        max_length=30
    )

    assigned_team: Optional[str] = Field(
        default=None,
        max_length=120
    )


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


class EmergencyStatusUpdate(DisasterMeshSchema):
    status: str = Field(
        min_length=1,
        max_length=30
    )

    assigned_team: Optional[str] = Field(
        default=None,
        max_length=120
    )


# =========================================================
# Route Schemas
# =========================================================

class RouteCreate(DisasterMeshSchema):
    source: int
    destination: int
    next_hop: int
    hop_count: int = Field(
        default=1,
        ge=1
    )
    quality: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )
    status: str = Field(
        default="ACTIVE",
        max_length=30
    )


class RouteResponse(DisasterMeshSchema):
    route_id: int
    source: int
    destination: int
    next_hop: int
    hop_count: int
    quality: Optional[float] = None
    status: str
    updated_at: datetime


# =========================================================
# Log Schemas
# =========================================================

class LogCreate(DisasterMeshSchema):
    node_id: Optional[int] = None

    event_type: str = Field(
        min_length=1,
        max_length=50
    )

    description: str = Field(
        min_length=1,
        max_length=2000
    )


class LogResponse(DisasterMeshSchema):
    log_id: int
    node_id: Optional[int] = None
    event_type: str
    description: str
    timestamp: datetime


# =========================================================
# System Status
# =========================================================

class SystemStatusResponse(DisasterMeshSchema):
    system: str
    backend: str
    database: str
    status: str

# =========================================================
# Node Status Response
# =========================================================

class NodeStatusResponse(DisasterMeshSchema):
    total_nodes: int
    online_nodes: int
    offline_nodes: int
    stale_nodes: int