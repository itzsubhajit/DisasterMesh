from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_operator_or_admin
from ..models import Log, Node, User
from ..schemas import LogCreate, LogResponse


router = APIRouter(prefix="/api/logs", tags=["Audit Logs"])


@router.post(
    "",
    response_model=LogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_log(
    data: LogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    if data.node_id is not None:
        node = db.query(Node).filter(Node.node_id == data.node_id).first()
        if node is None:
            raise HTTPException(status_code=404, detail="Node not found.")

    log = Log(
        node_id=data.node_id,
        event_type=data.event_type.strip().upper(),
        description=data.description.strip(),
    )

    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[LogResponse])
def get_logs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Log)
        .order_by(Log.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )