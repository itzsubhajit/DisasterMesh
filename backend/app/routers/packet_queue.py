
from datetime import datetime, timezone, timedelta
from typing import Optional
from threading import Lock
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_operator_or_admin
from ..models import Message, Node, User, Log
from ..queue_models import PacketQueue
from ..schemas import (
    PacketQueueCreate,
    PacketQueueResponse,
    PacketQueueStatsResponse,
    PacketQueueProcessResponse,
)


router = APIRouter(
    prefix="/api/queue",
    tags=["Packet Queue"],
)

VALID_STATUSES = {
    "QUEUED",
    "SYNCING",
    "SYNCED",
    "FAILED",
    "EXPIRED",
}


_queue_processing_lock = Lock()
def utc_now():
    return datetime.now(timezone.utc)


def normalize_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


# =========================================================
# ENQUEUE PACKET
# =========================================================

@router.post(
    "/enqueue",
    response_model=PacketQueueResponse,
    status_code=status.HTTP_201_CREATED,
)
def enqueue_packet(
    data: PacketQueueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    """Persist a packet for later synchronization."""

    existing_queue_item = (
        db.query(PacketQueue)
        .filter(PacketQueue.message_id == data.message_id)
        .first()
    )

    if existing_queue_item is not None:
        raise HTTPException(
            status_code=409,
            detail="This message ID already exists in the packet queue.",
        )

    existing_message = (
        db.query(Message)
        .filter(Message.message_id == data.message_id)
        .first()
    )

    if existing_message is not None:
        raise HTTPException(
            status_code=409,
            detail="This message already exists in the main message database.",
        )

    sender = (
        db.query(Node)
        .filter(Node.node_id == data.sender_id)
        .first()
    )

    if sender is None:
        raise HTTPException(
            status_code=404,
            detail=f"Sender node '{data.sender_id}' was not found.",
        )

    if data.receiver_id is not None:
        receiver = (
            db.query(Node)
            .filter(Node.node_id == data.receiver_id)
            .first()
        )

        if receiver is None:
            raise HTTPException(
                status_code=404,
                detail=f"Receiver node '{data.receiver_id}' was not found.",
            )

    now = utc_now()

    item = PacketQueue(
        message_id=data.message_id,
        sender_id=data.sender_id,
        receiver_id=data.receiver_id,
        category=data.category.strip().upper(),
        priority=data.priority.strip().upper(),
        content=data.content.strip(),
        latitude=data.latitude,
        longitude=data.longitude,
        ttl=data.ttl,
        hop_count=data.hop_count,
        status="QUEUED",
        attempt_count=0,
        max_attempts=data.max_attempts,
        queued_at=now,
        next_retry_at=now,
        expires_at=now + timedelta(minutes=data.retention_minutes),
    )

    db.add(item)

    db.add(
        Log(
            node_id=data.sender_id,
            event_type="PACKET_QUEUED",
            description=(
                f"Packet {data.message_id} stored in the queue "
                f"by {current_user.username}."
            ),
        )
    )

    db.commit()
    db.refresh(item)

    return item


# =========================================================
# QUEUE STATISTICS
# =========================================================

@router.get(
    "/stats",
    response_model=PacketQueueStatsResponse,
)
def get_queue_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return packet queue statistics grouped by status."""

    rows = (
        db.query(
            PacketQueue.status,
            func.count(PacketQueue.queue_id),
        )
        .group_by(PacketQueue.status)
        .all()
    )

    counts = {
        queue_status.upper(): count
        for queue_status, count in rows
    }

    return PacketQueueStatsResponse(
        total_items=sum(counts.values()),
        queued_items=counts.get("QUEUED", 0),
        syncing_items=counts.get("SYNCING", 0),
        synced_items=counts.get("SYNCED", 0),
        failed_items=counts.get("FAILED", 0),
        expired_items=counts.get("EXPIRED", 0),
    )


# =========================================================
# LIST QUEUE ITEMS
# =========================================================

@router.get(
    "",
    response_model=list[PacketQueueResponse],
)
def get_queue_items(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return queue items, newest first."""

    query = db.query(PacketQueue)

    if status_filter is not None:
        normalized_status = status_filter.strip().upper()

        if normalized_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"Status must be one of {sorted(VALID_STATUSES)}.",
            )

        query = query.filter(
            func.upper(PacketQueue.status) == normalized_status
        )

    return (
        query
        .order_by(PacketQueue.queued_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )



# =========================================================
# PROCESS QUEUED PACKETS
# =========================================================

def process_queue_batch(
    db: Session,
    limit: int = 25,
) -> PacketQueueProcessResponse:
    """
    Shared processing function used by both the API endpoint
    and the automatic background worker.

    This synchronizes queued backend packets into the main
    message database. It does not perform physical LoRa transmission.
    """

    with _queue_processing_lock:

        now = utc_now()

        items = (
            db.query(PacketQueue)
            .filter(
                PacketQueue.status == "QUEUED",
                or_(
                    PacketQueue.next_retry_at.is_(None),
                    PacketQueue.next_retry_at <= now,
                    PacketQueue.expires_at <= now,
                ),
            )
            .order_by(PacketQueue.queued_at.asc())
            .limit(limit)
            .all()
        )

        checked = 0
        synced = 0
        retry_scheduled = 0
        failed = 0
        expired = 0

        for item in items:

            checked += 1
            now = utc_now()
            queue_id = item.queue_id

            # Check packet expiry
            if (
                item.expires_at is not None
                and normalize_utc(item.expires_at) <= now
            ):
                item.status = "EXPIRED"
                item.last_error = (
                    "Packet retention period expired before synchronization."
                )

                db.commit()
                expired += 1
                continue

            attempt_number = item.attempt_count + 1

            # Check maximum processing attempts
            if attempt_number > item.max_attempts:

                item.status = "FAILED"
                item.last_error = (
                    "Maximum processing attempts exceeded."
                )

                db.commit()
                failed += 1
                continue

            try:

                item.status = "SYNCING"
                item.attempt_count = attempt_number
                item.last_attempt_at = now

                # Prevent duplicate message creation
                existing_message = (
                    db.query(Message)
                    .filter(
                        Message.message_id == item.message_id
                    )
                    .first()
                )

                if existing_message is None:

                    message = Message(
                        message_id=item.message_id,
                        sender_id=item.sender_id,
                        receiver_id=item.receiver_id,
                        category=item.category,
                        priority=item.priority,
                        content=item.content,
                        latitude=item.latitude,
                        longitude=item.longitude,
                        ttl=item.ttl,
                        hop_count=item.hop_count,
                        status="RECEIVED",
                    )

                    db.add(message)

                # Mark queue item synchronized
                item.status = "SYNCED"
                item.synced_at = now
                item.next_retry_at = None
                item.last_error = None

                db.add(
                    Log(
                        node_id=item.sender_id,
                        event_type="PACKET_SYNCED",
                        description=(
                            f"Queued packet {item.message_id} "
                            "synchronized into the main message database."
                        ),
                    )
                )

                db.commit()
                synced += 1

            except Exception as exc:

                db.rollback()

                failed_item = (
                    db.query(PacketQueue)
                    .filter(
                        PacketQueue.queue_id == queue_id
                    )
                    .first()
                )

                if failed_item is not None:

                    failed_item.attempt_count = attempt_number
                    failed_item.last_attempt_at = now
                    failed_item.last_error = str(exc)[:2000]

                    if attempt_number >= failed_item.max_attempts:

                        failed_item.status = "FAILED"
                        failed_item.next_retry_at = None
                        failed += 1

                    else:

                        failed_item.status = "QUEUED"

                        # Exponential backoff:
                        # 30, 60, 120, 240... seconds,
                        # with a maximum delay of one hour.
                        delay_seconds = min(
                            30 * (2 ** (attempt_number - 1)),
                            3600,
                        )

                        failed_item.next_retry_at = (
                            now + timedelta(seconds=delay_seconds)
                        )

                        retry_scheduled += 1

                    db.commit()

        return PacketQueueProcessResponse(
            checked=checked,
            synced=synced,
            retry_scheduled=retry_scheduled,
            failed=failed,
            expired=expired,
        )


@router.post(
    "/process",
    response_model=PacketQueueProcessResponse,
)
def process_queue(
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    """
    Manually process pending buffered packets.

    This uses the same processing function as the background worker.
    """

    return process_queue_batch(db=db, limit=limit)


# =========================================================
# MANUAL RETRY
# =========================================================

@router.post(
    "/{queue_id}/retry",
    response_model=PacketQueueResponse,
)
def retry_queue_item(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    """Requeue one failed packet for an additional processing attempt."""

    item = (
        db.query(PacketQueue)
        .filter(PacketQueue.queue_id == queue_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Packet queue item not found.",
        )

    if item.status != "FAILED":
        raise HTTPException(
            status_code=409,
            detail="Only failed queue items can be manually retried.",
        )

    now = utc_now()

    if (
        item.expires_at is not None
        and normalize_utc(item.expires_at) <= now
    ):
        item.status = "EXPIRED"
        db.commit()
        db.refresh(item)

        raise HTTPException(
            status_code=409,
            detail="This packet has expired and cannot be retried.",
        )

    item.status = "QUEUED"

    # Preserve historical attempts and grant one additional attempt.
    item.max_attempts += 1

    item.next_retry_at = now
    item.last_error = None

    db.add(
        Log(
            node_id=item.sender_id,
            event_type="PACKET_REQUEUED",
            description=(
                f"Packet {item.message_id} manually requeued "
                f"by {current_user.username}."
            ),
        )
    )

    db.commit()
    db.refresh(item)

    return item


# =========================================================
# GET ONE QUEUE ITEM
# =========================================================

@router.get(
    "/{queue_id}",
    response_model=PacketQueueResponse,
)
def get_queue_item(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return details for one queued packet."""

    item = (
        db.query(PacketQueue)
        .filter(PacketQueue.queue_id == queue_id)
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Packet queue item not found.",
        )

    return item
