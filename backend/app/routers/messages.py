
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Message, Node, User
from ..schemas import MessageCreate, MessageResponse


router = APIRouter(prefix="/api/messages", tags=["Messages"])


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Store a new message received by the DisasterMesh backend."""

    existing_message = (
        db.query(Message)
        .filter(Message.message_id == message_data.message_id)
        .first()
    )

    if existing_message is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A message with this message_id already exists.",
        )

    sender = (
        db.query(Node)
        .filter(Node.node_id == message_data.sender_id)
        .first()
    )

    if sender is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sender node '{message_data.sender_id}' was not found.",
        )

    if message_data.receiver_id is not None:
        receiver = (
            db.query(Node)
            .filter(Node.node_id == message_data.receiver_id)
            .first()
        )

        if receiver is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Receiver node '{message_data.receiver_id}' "
                    "was not found."
                ),
            )

    message = Message(
        message_id=message_data.message_id,
        sender_id=message_data.sender_id,
        receiver_id=message_data.receiver_id,
        category=message_data.category.strip().upper(),
        priority=message_data.priority.strip().upper(),
        content=message_data.content.strip(),
        latitude=message_data.latitude,
        longitude=message_data.longitude,
        ttl=message_data.ttl,
        hop_count=message_data.hop_count,
        status="RECEIVED",
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get(
    "",
    response_model=list[MessageResponse],
)
def get_messages(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent messages, newest first."""

    return (
        db.query(Message)
        .order_by(Message.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post(
    "/{message_id}/ack",
    response_model=MessageResponse,
)
def acknowledge_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Acknowledge a stored message. Repeated ACK requests are safe."""

    message = (
        db.query(Message)
        .filter(Message.message_id == message_id)
        .first()
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message '{message_id}' was not found.",
        )

    message.status = "ACKNOWLEDGED"
    db.commit()
    db.refresh(message)
    return message


@router.get(
    "/{message_id}",
    response_model=MessageResponse,
)
def get_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return details for one message."""

    message = (
        db.query(Message)
        .filter(Message.message_id == message_id)
        .first()
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message '{message_id}' was not found.",
        )

    return message
