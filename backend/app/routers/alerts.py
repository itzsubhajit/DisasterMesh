
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_operator_or_admin
from ..models import EmergencyRequest, Log, Node, User
from ..queue_models import PacketQueue
from ..alert_models import Alert


router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

STALE_AFTER = timedelta(minutes=5)
LOW_BATTERY_THRESHOLD = 20

VALID_ALERT_STATUSES = {
    "OPEN",
    "ACKNOWLEDGED",
    "RESOLVED",
}

VALID_SEVERITIES = {
    "CRITICAL",
    "HIGH",
    "WARNING",
    "INFO",
}


def utc_now():
    return datetime.now(timezone.utc)


def normalize_utc(value):
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def add_condition(conditions, fingerprint, **details):
    conditions[fingerprint] = details


def audit_alert(db, alert, event_type, username):
    node_id = None

    if alert.source_type in {"NODE", "GATEWAY"}:
        node_id = alert.source_id

    db.add(
        Log(
            node_id=node_id,
            event_type=event_type,
            description=(
                f"Alert #{alert.alert_id} ({alert.alert_type}) "
                f"was {event_type.lower().replace('_', ' ')} "
                f"by {username}."
            ),
        )
    )


# =========================================================
# SCAN SYSTEM FOR ALERT CONDITIONS
# =========================================================

@router.post("/scan")
def scan_alert_conditions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    """
    Detect current system alert conditions.

    This is an on-demand scan. A background scheduler may be added
    later to execute it automatically.
    """

    now = utc_now()
    conditions = {}

    # -----------------------------------------------------
    # Node health alerts
    # -----------------------------------------------------

    nodes = db.query(Node).all()

    gateway_nodes = [
        node
        for node in nodes
        if (node.node_type or "").upper() == "GATEWAY"
    ]

    for node in nodes:
        node_status = (node.status or "").upper()
        is_gateway = (node.node_type or "").upper() == "GATEWAY"

        last_seen = normalize_utc(node.last_seen)

        is_stale = (
            last_seen is None
            or now - last_seen > STALE_AFTER
        )

        if node_status == "OFFLINE":
            if is_gateway:
                alert_type = "GATEWAY_OFFLINE"
                severity = "CRITICAL"
                title = f"Gateway {node.node_id} is offline"
            else:
                alert_type = "NODE_OFFLINE"
                severity = "HIGH"
                title = f"Node {node.node_id} is offline"

            add_condition(
                conditions,
                f"{alert_type}:{node.node_id}",
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=(
                    f"Node {node.node_id} has reported an OFFLINE status."
                ),
                source_type="GATEWAY" if is_gateway else "NODE",
                source_id=node.node_id,
            )

        elif is_stale:
            if is_gateway:
                alert_type = "GATEWAY_STALE"
                severity = "HIGH"
                title = f"Gateway {node.node_id} is stale"
            else:
                alert_type = "NODE_STALE"
                severity = "WARNING"
                title = f"Node {node.node_id} has stopped reporting"

            add_condition(
                conditions,
                f"{alert_type}:{node.node_id}",
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=(
                    f"Node {node.node_id} has not sent a heartbeat "
                    "within the configured five-minute threshold."
                ),
                source_type="GATEWAY" if is_gateway else "NODE",
                source_id=node.node_id,
            )

        if (
            node.battery_level is not None
            and node.battery_level <= LOW_BATTERY_THRESHOLD
        ):
            add_condition(
                conditions,
                f"LOW_BATTERY:{node.node_id}",
                alert_type="LOW_BATTERY",
                severity="WARNING",
                title=f"Low battery on {node.node_id}",
                description=(
                    f"Node {node.node_id} battery is "
                    f"{node.battery_level:.1f}%. "
                    f"Threshold: {LOW_BATTERY_THRESHOLD}%."
                ),
                source_type="NODE",
                source_id=node.node_id,
            )

    # -----------------------------------------------------
    # Gateway registration alert
    # -----------------------------------------------------

    if not gateway_nodes:
        add_condition(
            conditions,
            "GATEWAY_NOT_REGISTERED:system",
            alert_type="GATEWAY_NOT_REGISTERED",
            severity="WARNING",
            title="No gateway node is registered",
            description=(
                "No node with node_type GATEWAY is registered. "
                "Physical gateway availability cannot be verified."
            ),
            source_type="SYSTEM",
            source_id="system",
        )

    # -----------------------------------------------------
    # Critical emergency alerts
    # -----------------------------------------------------

    emergencies = (
        db.query(EmergencyRequest)
        .filter(
            func.upper(EmergencyRequest.priority) == "CRITICAL",
            func.upper(EmergencyRequest.status).notin_(
                ["RESOLVED", "CANCELLED"]
            ),
        )
        .all()
    )

    for emergency in emergencies:
        add_condition(
            conditions,
            f"CRITICAL_EMERGENCY:{emergency.request_id}",
            alert_type="CRITICAL_EMERGENCY",
            severity="CRITICAL",
            title=f"Critical emergency #{emergency.request_id}",
            description=(
                f"Critical {emergency.category} emergency "
                f"#{emergency.request_id} is currently "
                f"{emergency.status}."
            ),
            source_type="EMERGENCY",
            source_id=str(emergency.request_id),
        )

    # -----------------------------------------------------
    # Failed and expired packet alerts
    # -----------------------------------------------------

    queue_items = (
        db.query(PacketQueue)
        .filter(
            func.upper(PacketQueue.status).in_(["FAILED", "EXPIRED"])
        )
        .all()
    )

    for item in queue_items:
        queue_status = item.status.upper()

        if queue_status == "FAILED":
            alert_type = "PACKET_SYNC_FAILED"
            severity = "HIGH"
            title = f"Packet synchronization failed: {item.message_id}"
            description = (
                f"Packet {item.message_id} failed after "
                f"{item.attempt_count} attempts. "
                f"Last error: {item.last_error or 'Not specified'}"
            )
        else:
            alert_type = "PACKET_EXPIRED"
            severity = "WARNING"
            title = f"Packet expired: {item.message_id}"
            description = (
                f"Packet {item.message_id} exceeded its retention period."
            )

        add_condition(
            conditions,
            f"{alert_type}:{item.queue_id}",
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            source_type="PACKET_QUEUE",
            source_id=str(item.queue_id),
        )

    # -----------------------------------------------------
    # Create, update, reopen and resolve alerts
    # -----------------------------------------------------

    existing_alerts = db.query(Alert).all()

    alerts_by_fingerprint = {
        alert.fingerprint: alert
        for alert in existing_alerts
    }

    created = 0
    reopened = 0
    resolved = 0

    for fingerprint, details in conditions.items():
        alert = alerts_by_fingerprint.get(fingerprint)

        if alert is None:
            alert = Alert(
                fingerprint=fingerprint,
                status="OPEN",
                created_at=now,
                last_triggered_at=now,
                occurrence_count=1,
                **details,
            )

            db.add(alert)
            db.flush()

            audit_alert(
                db,
                alert,
                "ALERT_CREATED",
                current_user.username,
            )

            created += 1
            continue

        alert.last_triggered_at = now
        alert.title = details["title"]
        alert.description = details["description"]
        alert.severity = details["severity"]

        if alert.status == "RESOLVED":
            alert.status = "OPEN"
            alert.acknowledged_at = None
            alert.resolved_at = None
            alert.occurrence_count += 1

            audit_alert(
                db,
                alert,
                "ALERT_REOPENED",
                current_user.username,
            )

            reopened += 1

    for alert in existing_alerts:
        if (
            alert.fingerprint not in conditions
            and alert.status in {"OPEN", "ACKNOWLEDGED"}
        ):
            alert.status = "RESOLVED"
            alert.resolved_at = now

            audit_alert(
                db,
                alert,
                "ALERT_AUTO_RESOLVED",
                current_user.username,
            )

            resolved += 1

    db.commit()

    active_count = (
        db.query(Alert)
        .filter(Alert.status.in_(["OPEN", "ACKNOWLEDGED"]))
        .count()
    )

    return {
        "scan_time": now.isoformat(),
        "conditions_detected": len(conditions),
        "alerts_created": created,
        "alerts_reopened": reopened,
        "alerts_auto_resolved": resolved,
        "active_alerts": active_count,
    }


# =========================================================
# ALERT STATISTICS
# =========================================================

@router.get("/stats")
def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Alert.status, func.count(Alert.alert_id))
        .group_by(Alert.status)
        .all()
    )

    status_counts = {
        key.upper(): value
        for key, value in rows
    }

    severity_rows = (
        db.query(Alert.severity, func.count(Alert.alert_id))
        .group_by(Alert.severity)
        .all()
    )

    severity_counts = {
        key.upper(): value
        for key, value in severity_rows
    }

    return {
        "total_alerts": sum(status_counts.values()),
        "open_alerts": status_counts.get("OPEN", 0),
        "acknowledged_alerts": status_counts.get("ACKNOWLEDGED", 0),
        "resolved_alerts": status_counts.get("RESOLVED", 0),
        "by_severity": severity_counts,
    }


# =========================================================
# LIST ALERTS
# =========================================================

@router.get("")
def get_alerts(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    severity_filter: Optional[str] = Query(default=None, alias="severity"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Alert)

    if status_filter:
        normalized = status_filter.strip().upper()

        if normalized not in VALID_ALERT_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"Status must be one of {sorted(VALID_ALERT_STATUSES)}.",
            )

        query = query.filter(func.upper(Alert.status) == normalized)

    if severity_filter:
        normalized = severity_filter.strip().upper()

        if normalized not in VALID_SEVERITIES:
            raise HTTPException(
                status_code=422,
                detail=f"Severity must be one of {sorted(VALID_SEVERITIES)}.",
            )

        query = query.filter(func.upper(Alert.severity) == normalized)

    return (
        query
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# =========================================================
# GET ONE ALERT
# =========================================================

@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = (
        db.query(Alert)
        .filter(Alert.alert_id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    return alert


# =========================================================
# ACKNOWLEDGE ALERT
# =========================================================

@router.put("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    alert = (
        db.query(Alert)
        .filter(Alert.alert_id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    if alert.status == "RESOLVED":
        raise HTTPException(
            status_code=409,
            detail="A resolved alert cannot be acknowledged.",
        )

    if alert.status == "OPEN":
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = utc_now()

        audit_alert(
            db,
            alert,
            "ALERT_ACKNOWLEDGED",
            current_user.username,
        )

        db.commit()
        db.refresh(alert)

    return alert


# =========================================================
# RESOLVE ALERT
# =========================================================

@router.put("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    alert = (
        db.query(Alert)
        .filter(Alert.alert_id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    if alert.status == "RESOLVED":
        return alert

    alert.status = "RESOLVED"
    alert.resolved_at = utc_now()

    audit_alert(
        db,
        alert,
        "ALERT_RESOLVED",
        current_user.username,
    )

    db.commit()
    db.refresh(alert)

    return alert
