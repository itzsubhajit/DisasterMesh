
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import (
    EmergencyRequest,
    Message,
    Node,
    Route,
    User,
)
from ..queue_models import PacketQueue
from ..alert_models import Alert


router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

STALE_AFTER = timedelta(minutes=5)


def normalize_utc(value):
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def grouped_counts(db, column):
    rows = (
        db.query(column, func.count())
        .group_by(column)
        .all()
    )

    return {
        str(key or "UNKNOWN").upper(): count
        for key, count in rows
    }


def calculate_node_health(nodes):
    now = datetime.now(timezone.utc)

    online = 0
    offline = 0
    stale = 0
    low_battery = 0
    other = 0

    for node in nodes:
        node_status = (node.status or "").upper()

        if (
            node.battery_level is not None
            and node.battery_level <= 20
        ):
            low_battery += 1

        if node_status == "OFFLINE":
            offline += 1
            continue

        last_seen = normalize_utc(node.last_seen)

        is_stale = (
            last_seen is None
            or now - last_seen > STALE_AFTER
        )

        if is_stale:
            stale += 1
        elif node_status == "ONLINE":
            online += 1
        else:
            other += 1

    return {
        "total_nodes": len(nodes),
        "online_nodes": online,
        "offline_nodes": offline,
        "stale_nodes": stale,
        "other_nodes": other,
        "low_battery_nodes": low_battery,
    }


def calculate_queue_counts(db):
    values = grouped_counts(db, PacketQueue.status)

    return {
        "total_items": sum(values.values()),
        "queued_items": values.get("QUEUED", 0),
        "syncing_items": values.get("SYNCING", 0),
        "synced_items": values.get("SYNCED", 0),
        "failed_items": values.get("FAILED", 0),
        "expired_items": values.get("EXPIRED", 0),
        "by_status": values,
    }


# =========================================================
# OVERALL DASHBOARD ANALYTICS
# =========================================================

@router.get("/overview")
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    nodes = db.query(Node).all()
    node_stats = calculate_node_health(nodes)

    total_messages = db.query(Message).count()
    total_incidents = db.query(EmergencyRequest).count()
    total_routes = db.query(Route).count()

    active_incidents = (
        db.query(EmergencyRequest)
        .filter(
            func.upper(EmergencyRequest.status).notin_(
                ["RESOLVED", "CANCELLED"]
            )
        )
        .count()
    )

    resolved_incidents = (
        db.query(EmergencyRequest)
        .filter(
            func.upper(EmergencyRequest.status) == "RESOLVED"
        )
        .count()
    )

    cancelled_incidents = (
        db.query(EmergencyRequest)
        .filter(
            func.upper(EmergencyRequest.status) == "CANCELLED"
        )
        .count()
    )

    active_routes = (
        db.query(Route)
        .filter(func.upper(Route.status) == "ACTIVE")
        .count()
    )

    alert_counts = grouped_counts(db, Alert.status)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "nodes": node_stats,

        "messages": {
            "total_messages": total_messages,
            "by_status": grouped_counts(db, Message.status),
            "by_priority": grouped_counts(db, Message.priority),
        },

        "incidents": {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "resolved_incidents": resolved_incidents,
            "cancelled_incidents": cancelled_incidents,
        },

        "network": {
            "total_routes": total_routes,
            "active_routes": active_routes,
        },

        "queue": calculate_queue_counts(db),

        "alerts": {
            "total_alerts": sum(alert_counts.values()),
            "open_alerts": alert_counts.get("OPEN", 0),
            "acknowledged_alerts": alert_counts.get(
                "ACKNOWLEDGED", 0
            ),
            "resolved_alerts": alert_counts.get("RESOLVED", 0),
        },
    }


# =========================================================
# INCIDENT ANALYTICS
# =========================================================

@router.get("/incidents")
def get_incident_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(EmergencyRequest).count()

    active = (
        db.query(EmergencyRequest)
        .filter(
            func.upper(EmergencyRequest.status).notin_(
                ["RESOLVED", "CANCELLED"]
            )
        )
        .count()
    )

    resolved = (
        db.query(EmergencyRequest)
        .filter(
            func.upper(EmergencyRequest.status) == "RESOLVED"
        )
        .count()
    )

    critical = (
        db.query(EmergencyRequest)
        .filter(
            func.upper(EmergencyRequest.priority) == "CRITICAL"
        )
        .count()
    )

    return {
        "total_incidents": total,
        "active_incidents": active,
        "resolved_incidents": resolved,
        "critical_incidents": critical,
        "by_status": grouped_counts(
            db,
            EmergencyRequest.status,
        ),
        "by_priority": grouped_counts(
            db,
            EmergencyRequest.priority,
        ),
        "by_category": grouped_counts(
            db,
            EmergencyRequest.category,
        ),
    }


# =========================================================
# NODE ANALYTICS
# =========================================================

@router.get("/nodes")
def get_node_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    nodes = db.query(Node).all()

    by_type = grouped_counts(db, Node.node_type)

    return {
        **calculate_node_health(nodes),
        "by_type": by_type,
    }


# =========================================================
# MESSAGE ANALYTICS
# =========================================================

@router.get("/messages")
def get_message_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "total_messages": db.query(Message).count(),
        "by_status": grouped_counts(db, Message.status),
        "by_priority": grouped_counts(db, Message.priority),
        "by_category": grouped_counts(db, Message.category),
    }


# =========================================================
# NETWORK ANALYTICS
# =========================================================

@router.get("/network")
def get_network_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_routes = db.query(Route).count()

    active_routes = (
        db.query(Route)
        .filter(func.upper(Route.status) == "ACTIVE")
        .count()
    )

    standby_routes = (
        db.query(Route)
        .filter(func.upper(Route.status) == "STANDBY")
        .count()
    )

    inactive_routes = (
        db.query(Route)
        .filter(func.upper(Route.status) == "INACTIVE")
        .count()
    )

    average_quality = db.query(
        func.avg(Route.quality)
    ).scalar()

    average_hops = db.query(
        func.avg(Route.hop_count)
    ).scalar()

    gateway_count = (
        db.query(Node)
        .filter(func.upper(Node.node_type) == "GATEWAY")
        .count()
    )

    return {
        "total_routes": total_routes,
        "active_routes": active_routes,
        "standby_routes": standby_routes,
        "inactive_routes": inactive_routes,
        "average_route_quality": (
            round(float(average_quality), 2)
            if average_quality is not None
            else None
        ),
        "average_hop_count": (
            round(float(average_hops), 2)
            if average_hops is not None
            else None
        ),
        "registered_gateways": gateway_count,
        "by_status": grouped_counts(db, Route.status),
    }


# =========================================================
# PACKET QUEUE ANALYTICS
# =========================================================

@router.get("/queue")
def get_queue_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return calculate_queue_counts(db)
