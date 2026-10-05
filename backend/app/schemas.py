"""
DisasterMesh Backend
Step 36 - Pydantic API Schemas

These schemas define the request and response contracts used by the
DisasterMesh REST API.

The fields follow the project report/SRS entities and API requirements:
Users, Nodes, Messages, Routes, EmergencyRequests, Logs.

Pydantic v2 is used because the backend environment contains the current
Pydantic release installed during Step 32.
"""

from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ===========================================================================
# COMMON ENUM-LIKE VALIDATION VALUES
# ===========================================================================

VALID_ROLES = {
    "ADMIN",
    "OPERATOR",
}

VALID_NODE_TYPES = {
    "FIELD",
    "RELAY",
    "GATEWAY",
}

VALID_NODE_STATUSES = {
    "ONLINE",
    "OFFLINE",
    "STALE",
}

VALID_PRIORITIES = {
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
}

VALID_MESSAGE_STATUSES = {
    "CREATED",
    "FORWARDED",
    "DELIVERED",
    "QUEUED",
    "RETRY_READY",
    "FAILED",
}

VALID_EMERGENCY_STATUSES = {
    "NEW",
    "ACKNOWLEDGED",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "CANCELLED",
}

VALID_ROUTE_STATUSES = {
    "ACTIVE",
    "STANDBY",
    "STALE",
}

VALID_LOG_SEVERITIES = {
    "INFO",
    "WARNING",
    "CRITICAL",
}


# ===========================================================================
# BASE SCHEMA
# ===========================================================================

class DisasterMeshSchema(BaseModel):
    """
    Common base configuration for API schemas.
    """

    model_config = ConfigDict(
        from_attributes=True
    )


# ===========================================================================
# AUTHENTICATION
# ===========================================================================

class LoginRequest(DisasterMeshSchema):
    """
    POST /api/auth/login request.

    The report requires dashboard authentication with username and
    password and specifies JWT as the authentication mechanism.
    """

    username: str = Field(
        min_length=1,
        max_length=80
    )

    password: str = Field(
        min_length=1,
        max_length=255
    )


class LoginResponse(DisasterMeshSchema):
    """
    Successful authentication response.
    """

    access_token: str
    token_type: str = "bearer"
    username: str
    name: str
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:

        value = value.upper()

        if value not in VALID_ROLES:
            raise ValueError(
                f"role must be one of: {', '.join(sorted(VALID_ROLES))}"
            )

        return value


# ===========================================================================
# USER MANAGEMENT
# ===========================================================================

class UserCreateRequest(DisasterMeshSchema):
    """
    Administrator-created dashboard user.
    """

    name: str = Field(
        min_length=2,
        max_length=120
    )

    username: str = Field(
        min_length=3,
        max_length=80
    )

    password: str = Field(
        min_length=6,
        max_length=255
    )

    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:

        value = value.upper()

        if value not in VALID_ROLES:
            raise ValueError(
                f"role must be one of: {', '.join(sorted(VALID_ROLES))}"
            )

        return value


class UserResponse(DisasterMeshSchema):
    """
    Public user representation.

    Password hashes are intentionally never exposed through this schema.
    """

    user_id: int
    name: str
    role: str
    username: str
    created_at: datetime


# ===========================================================================
# NODES
# ===========================================================================

class NodeRegisterRequest(DisasterMeshSchema):
    """
    POST /api/nodes/register request.
    """

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
        min_length=2,
        max_length=30
    )

    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180
    )

    battery_level: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    status: str = "ONLINE"

    @field_validator("node_type")
    @classmethod
    def validate_node_type(cls, value: str) -> str:

        value = value.upper()

        if value not in VALID_NODE_TYPES:
            raise ValueError(
                f"node_type must be one of: {', '.join(sorted(VALID_NODE_TYPES))}"
            )

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:

        value = value.upper()

        if value not in VALID_NODE_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(VALID_NODE_STATUSES))}"
            )

        return value


class NodeResponse(DisasterMeshSchema):
    """
    Node returned by the backend.
    """

    node_id: str
    device_id: str
    node_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery_level: Optional[float] = None
    status: str
    last_seen: Optional[datetime] = None


class NodeStatusResponse(DisasterMeshSchema):
    """
    GET /api/nodes/status summary.
    """

    total_nodes: int
    online_nodes: int
    offline_nodes: int
    stale_nodes: int


# ===========================================================================
# MESSAGES
# ===========================================================================

class MessageCreateRequest(DisasterMeshSchema):
    """
    POST /api/messages request.

    This represents the logical emergency packet arriving at the backend.
    """

    message_id: str = Field(
        min_length=3,
        max_length=100
    )

    sender_id: str = Field(
        min_length=2,
        max_length=50
    )

    receiver_id: Optional[str] = Field(
        default=None,
        max_length=50
    )

    category: str = Field(
        min_length=2,
        max_length=50
    )

    priority: str

    content: str = Field(
        min_length=1,
        max_length=5000
    )

    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180
    )

    timestamp: Optional[datetime] = None

    ttl: int = Field(
        default=5,
        ge=0,
        le=255
    )

    hop_count: int = Field(
        default=0,
        ge=0
    )

    status: str = "CREATED"

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:

        value = value.upper()

        if value not in VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}"
            )

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:

        value = value.upper()

        if value not in VALID_MESSAGE_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(VALID_MESSAGE_STATUSES))}"
            )

        return value


class MessageResponse(DisasterMeshSchema):
    """
    Stored message returned by the backend.
    """

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


class MessageAckResponse(DisasterMeshSchema):
    """
    POST /api/messages/{id}/ack response.
    """

    message_id: str
    acknowledged: bool
    acknowledged_at: datetime


# ===========================================================================
# EMERGENCY REQUESTS
# ===========================================================================

class EmergencyStatusUpdateRequest(DisasterMeshSchema):
    """
    PUT /api/emergency/{id}/status request.
    """

    status: str

    assigned_team: Optional[str] = Field(
        default=None,
        max_length=100
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:

        value = value.upper()

        if value not in VALID_EMERGENCY_STATUSES:
            raise ValueError(
                "status must be one of: "
                f"{', '.join(sorted(VALID_EMERGENCY_STATUSES))}"
            )

        return value


class EmergencyRequestResponse(DisasterMeshSchema):
    """
    Operator-facing emergency request.
    """

    request_id: int
    message_id: str
    category: str
    priority: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    assigned_team: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


# ===========================================================================
# ROUTES
# ===========================================================================

class RouteResponse(DisasterMeshSchema):
    """
    GET /api/routes response.
    """

    route_id: int
    source: str
    destination: str
    next_hop: Optional[str] = None
    hop_count: int
    quality: Optional[float] = None
    status: str
    updated_at: datetime


# ===========================================================================
# LOGS
# ===========================================================================

class LogResponse(DisasterMeshSchema):
    """
    Backend audit/operational log representation.
    """

    log_id: int
    node_id: Optional[str] = None
    event_type: str
    description: str
    timestamp: datetime


# ===========================================================================
# SYSTEM HEALTH
# ===========================================================================

class SystemStatusResponse(DisasterMeshSchema):
    """
    GET /api/system/status response.

    This will later feed the existing Gateway/System Health views in
    the frontend.
    """

    mesh_status: str
    gateway_status: str
    backend_status: str
    database_status: str
    ai_status: str
    gps_status: str
    queue_status: str
    logging_status: str


# ===========================================================================
# GENERIC API RESPONSE
# ===========================================================================

class APIMessageResponse(DisasterMeshSchema):
    """
    Simple status/message response for API operations.
    """

    success: bool
    message: str
