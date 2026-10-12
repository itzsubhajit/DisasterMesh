from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Message, Node, User


router = APIRouter(prefix="/api/gateway", tags=["Gateway"])


@router.get("/status")
def get_gateway_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    gateway = (
        db.query(Node)
        .filter(func.upper(Node.node_type) == "GATEWAY")
        .order_by(Node.last_seen.desc())
        .first()
    )

    now = datetime.now(timezone.utc)
    stale_after = timedelta(minutes=5)

    pending_sync = (
        db.query(Message)
        .filter(
            func.upper(Message.status).in_(
                ["QUEUED", "PENDING_SYNC", "BUFFERED"]
            )
        )
        .count()
    )

    if gateway is None:
        gateway_status = "NOT_REGISTERED"
        connected = False
        last_seen = None
        gateway_node_id = None
    else:
        last_seen_value = gateway.last_seen

        if last_seen_value is not None and last_seen_value.tzinfo is None:
            last_seen_value = last_seen_value.replace(tzinfo=timezone.utc)

        last_seen = (
            last_seen_value.isoformat()
            if last_seen_value is not None
            else None
        )
        gateway_node_id = gateway.node_id

        if (gateway.status or "").upper() == "OFFLINE":
            gateway_status = "OFFLINE"
        elif (
            last_seen_value is None
            or now - last_seen_value > stale_after
        ):
            gateway_status = "STALE"
        else:
            gateway_status = "CONNECTED"

        connected = gateway_status == "CONNECTED"

    return {
        "gateway_node_id": gateway_node_id,
        "gateway_registered": gateway is not None,
        "gateway_connected": connected,
        "gateway_status": gateway_status,
        "last_seen": last_seen,
        "pending_sync_messages": pending_sync,
        "note": (
            "Connectivity is inferred from node heartbeat data. "
            "Physical gateway connectivity requires hardware integration."
        ),
    }