from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_operator_or_admin
from ..models import Log, Message, Node, User
from ..schemas import MessageCreate, MessageResponse

router = APIRouter(prefix="/api/messages", tags=["Messages"])


def classify_message_safely(content: str) -> dict:
    """Run the local classifier; fail closed to mandatory human review."""
    try:
        from ..ai.classifier import classify_emergency

        return classify_emergency(content)
    except Exception as exc:
        # Do not prevent the emergency message from being stored just because
        # a model/artifact is unavailable. Flag it for operator review instead.
        print(f"AI classification unavailable: {type(exc).__name__}: {exc}")
        return {
            "category": None,
            "category_confidence": None,
            "category_probabilities": None,
            "priority": None,
            "priority_confidence": None,
            "priority_probabilities": None,
            "requires_human_review": True,
            "review_reasons": ["AI_CLASSIFIER_UNAVAILABLE"],
            "matched_high_risk_phrases": [],
            "decision_authority": "HUMAN_OPERATOR",
            "model_info": {"status": "UNAVAILABLE"},
        }


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    """Store a message and attach AI recommendations for operator review."""

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

    sender = db.query(Node).filter(Node.node_id == message_data.sender_id).first()
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
                    f"Receiver node '{message_data.receiver_id}' was not found."
                ),
            )

    ai_result = classify_message_safely(message_data.content.strip())

    message = Message(
        message_id=message_data.message_id,
        sender_id=message_data.sender_id,
        receiver_id=message_data.receiver_id,
        # Keep original packet fields intact. AI suggestions are stored below.
        category=message_data.category.strip().upper(),
        priority=message_data.priority.strip().upper(),
        content=message_data.content.strip(),
        latitude=message_data.latitude,
        longitude=message_data.longitude,
        ttl=message_data.ttl,
        hop_count=message_data.hop_count,
        status="RECEIVED",
        ai_category=ai_result.get("category"),
        ai_category_confidence=ai_result.get("category_confidence"),
        ai_category_probabilities=ai_result.get("category_probabilities"),
        ai_priority=ai_result.get("priority"),
        ai_priority_confidence=ai_result.get("priority_confidence"),
        ai_priority_probabilities=ai_result.get("priority_probabilities"),
        ai_requires_human_review=bool(
            ai_result.get("requires_human_review", True)
        ),
        ai_review_reasons=ai_result.get("review_reasons") or [],
        ai_matched_high_risk_phrases=(
            ai_result.get("matched_high_risk_phrases") or []
        ),
        ai_decision_authority=ai_result.get(
            "decision_authority", "HUMAN_OPERATOR"
        ),
        ai_model_info=ai_result.get("model_info"),
    )

    db.add(message)
    db.add(
        Log(
            node_id=message.sender_id,
            event_type="AI_CLASSIFICATION_COMPLETED",
            description=(
                f"AI classification stored for message {message.message_id}; "
                f"human_review_required={message.ai_requires_human_review}."
            ),
        )
    )
    db.commit()
    db.refresh(message)
    return message


@router.get("", response_model=list[MessageResponse])
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


@router.post("/{message_id}/ack", response_model=MessageResponse)
def acknowledge_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
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


@router.get("/{message_id}", response_model=MessageResponse)
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
