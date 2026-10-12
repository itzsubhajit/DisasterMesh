
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_operator_or_admin
from ..models import EmergencyRequest, Log, Message, User
from ..schemas import EmergencyCreate, EmergencyResponse, EmergencyStatusUpdate

router = APIRouter(prefix="/api/emergency", tags=["Emergency Management"])

ALLOWED_TRANSITIONS = {
    "NEW": {"ACKNOWLEDGED", "CANCELLED"},
    "ACKNOWLEDGED": {"ASSIGNED", "CANCELLED"},
    "ASSIGNED": {"IN_PROGRESS", "CANCELLED"},
    "IN_PROGRESS": {"RESOLVED", "CANCELLED"},
    "RESOLVED": set(),
    "CANCELLED": set(),
}


def record_audit(db, node_id, event_type, description):
  db.add(
      Log(
          node_id=node_id,
          event_type=event_type,
          description=description,
      )
  )


@router.post(
    "",
    response_model=EmergencyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_emergency(
    data: EmergencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
  message = (
      db.query(Message).filter(Message.message_id == data.message_id).first()
  )

  if message is None:
    raise HTTPException(
        status_code=404,
        detail="The source message was not found.",
    )

  existing = (
      db.query(EmergencyRequest)
      .filter(EmergencyRequest.message_id == data.message_id)
      .first()
  )

  if existing is not None:
    raise HTTPException(
        status_code=409,
        detail="An emergency request already exists for this message.",
    )

  emergency = EmergencyRequest(
      message_id=data.message_id,
      category=data.category.strip().upper(),
      priority=data.priority.strip().upper(),
      latitude=data.latitude if data.latitude is not None else message.latitude,
      longitude=(
          data.longitude if data.longitude is not None else message.longitude
      ),
      status="NEW",
      assigned_team=None,
  )

  db.add(emergency)
  db.flush()

  record_audit(
      db,
      message.sender_id,
      "EMERGENCY_CREATED",
      f"Emergency request {emergency.request_id} created by"
      f" {current_user.username} from message {message.message_id}.",
  )

  db.commit()
  db.refresh(emergency)
  return emergency


@router.get("", response_model=list[EmergencyResponse])
def get_emergencies(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  return (
      db.query(EmergencyRequest)
      .order_by(EmergencyRequest.created_at.desc())
      .offset(offset)
      .limit(limit)
      .all()
  )


@router.get("/critical", response_model=list[EmergencyResponse])
def get_critical_emergencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  return (
      db.query(EmergencyRequest)
      .filter(
          func.upper(EmergencyRequest.priority) == "CRITICAL",
          func.upper(EmergencyRequest.status).notin_(
              ["RESOLVED", "CANCELLED"]
          ),
      )
      .order_by(EmergencyRequest.created_at.desc())
      .all()
  )


@router.get("/{request_id}", response_model=EmergencyResponse)
def get_emergency(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  emergency = (
      db.query(EmergencyRequest)
      .filter(EmergencyRequest.request_id == request_id)
      .first()
  )

  if emergency is None:
    raise HTTPException(status_code=404, detail="Emergency request not found.")

  return emergency


@router.put("/{request_id}/status", response_model=EmergencyResponse)
def update_emergency_status(
    request_id: int,
    data: EmergencyStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
  emergency = (
      db.query(EmergencyRequest)
      .filter(EmergencyRequest.request_id == request_id)
      .first()
  )

  if emergency is None:
    raise HTTPException(
        status_code=404,
        detail="Emergency request not found.",
    )

  old_status = emergency.status.upper()
  new_status = data.status.strip().upper()

  allowed_transitions = {
      "NEW": {"ACKNOWLEDGED", "CANCELLED"},
      "ACKNOWLEDGED": {"ASSIGNED", "CANCELLED"},
      "ASSIGNED": {"IN_PROGRESS", "CANCELLED"},
      "IN_PROGRESS": {"RESOLVED", "CANCELLED"},
      "RESOLVED": set(),
      "CANCELLED": set(),
  }

  if new_status not in allowed_transitions:
    raise HTTPException(
        status_code=422,
        detail="Invalid emergency status.",
    )

  if new_status == old_status:
    return emergency

  if new_status not in allowed_transitions[old_status]:
    raise HTTPException(
        status_code=409,
        detail=(
            f"Transition from {old_status} to {new_status} is not allowed."
        ),
    )

  if new_status == "ASSIGNED":
    if not data.assigned_team or not data.assigned_team.strip():
      raise HTTPException(
          status_code=422,
          detail="assigned_team is required when assigning an incident.",
      )
    emergency.assigned_team = data.assigned_team.strip()

  now = datetime.now(timezone.utc)

  if new_status == "ACKNOWLEDGED":
    emergency.acknowledged_at = now

  elif new_status == "ASSIGNED":
    emergency.assigned_at = now

  elif new_status == "RESOLVED":
    emergency.resolved_at = now

  emergency.status = new_status

  message = (
      db.query(Message).filter(Message.message_id == emergency.message_id).first()
  )

  record_audit(
      db,
      message.sender_id if message else None,
      "EMERGENCY_STATUS_CHANGED",
      f"Emergency request {request_id} changed from {old_status} to"
      f" {new_status} by {current_user.username}.",
  )

  db.commit()
  db.refresh(emergency)

  return emergency
