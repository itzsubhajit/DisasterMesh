
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Node, User
from ..schemas import (
    NodeCreate,
    NodeHeartbeat,
    NodeResponse,
    NodeStatusResponse,
)


router = APIRouter(prefix="/api/nodes", tags=["Nodes"])

STALE_THRESHOLD = timedelta(minutes=5)


def utc_now():
    return datetime.now(timezone.utc)


def normalized_utc(value: datetime) -> datetime:
    """Treat SQLite's naive timestamps as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@router.post(
    "/register",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_node(
    node_data: NodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a new field, relay, or gateway node."""

    existing_node = (
        db.query(Node)
        .filter(Node.node_id == node_data.node_id)
        .first()
    )
    if existing_node is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A node with this node_id is already registered.",
        )

    existing_device = (
        db.query(Node)
        .filter(Node.device_id == node_data.device_id)
        .first()
    )
    if existing_device is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A node with this device_id is already registered.",
        )

    node = Node(
        node_id=node_data.node_id,
        device_id=node_data.device_id,
        node_type=node_data.node_type,
        latitude=node_data.latitude,
        longitude=node_data.longitude,
        battery_level=node_data.battery_level,
        status=node_data.status.upper(),
        last_seen=utc_now(),
    )

    db.add(node)
    db.commit()
    db.refresh(node)
    return node


@router.post(
    "/{node_id}/heartbeat",
    response_model=NodeResponse,
)
def node_heartbeat(
    node_id: str,
    heartbeat: NodeHeartbeat,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a heartbeat and update any supplied node telemetry."""

    node = db.query(Node).filter(Node.node_id == node_id).first()

    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' was not found.",
        )

    if heartbeat.battery_level is not None:
        node.battery_level = heartbeat.battery_level

    if heartbeat.latitude is not None:
        node.latitude = heartbeat.latitude

    if heartbeat.longitude is not None:
        node.longitude = heartbeat.longitude

    node.last_seen = utc_now()
    node.status = "ONLINE"

    db.commit()
    db.refresh(node)
    return node


@router.get(
    "",
    response_model=list[NodeResponse],
)
def get_all_nodes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all registered nodes."""

    return db.query(Node).order_by(Node.node_id).all()


@router.get(
    "/status",
    response_model=NodeStatusResponse,
)
def get_node_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Summarize node health.

    ONLINE nodes that have not reported within five minutes are marked
    STALE. A subsequent heartbeat restores them to ONLINE.
    """

    nodes = db.query(Node).all()
    current_time = utc_now()

    online_nodes = 0
    offline_nodes = 0
    stale_nodes = 0
    changed = False

    for node in nodes:
        node_status = (node.status or "").upper()

        if node_status == "OFFLINE":
            offline_nodes += 1
            continue

        last_seen = (
            normalized_utc(node.last_seen)
            if node.last_seen is not None
            else None
        )

        is_stale = (
            last_seen is None
            or current_time - last_seen > STALE_THRESHOLD
        )

        if is_stale:
            stale_nodes += 1
            if node.status != "STALE":
                node.status = "STALE"
                changed = True
        elif node_status in {"ONLINE", "STALE"}:
            online_nodes += 1
            if node.status != "ONLINE":
                node.status = "ONLINE"
                changed = True
        else:
            offline_nodes += 1

    if changed:
        db.commit()

    return NodeStatusResponse(
        total_nodes=len(nodes),
        online_nodes=online_nodes,
        offline_nodes=offline_nodes,
        stale_nodes=stale_nodes,
    )


@router.get(
    "/{node_id}",
    response_model=NodeResponse,
)
def get_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return details for one registered node."""

    node = db.query(Node).filter(Node.node_id == node_id).first()

    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' was not found.",
        )

    return node
