from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_operator_or_admin
from ..models import Log, Node, Route, User
from ..schemas import RouteCreate, RouteResponse


router = APIRouter(prefix="/api/routes", tags=["Mesh Routes"])


@router.post(
    "",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_route(
    data: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin),
):
    source = db.query(Node).filter(Node.node_id == data.source).first()
    destination = (
        db.query(Node)
        .filter(Node.node_id == data.destination)
        .first()
    )

    if source is None or destination is None:
        raise HTTPException(
            status_code=404,
            detail="The source or destination node does not exist.",
        )

    if data.source == data.destination:
        raise HTTPException(
            status_code=422,
            detail="Source and destination must be different nodes.",
        )

    if data.next_hop is not None:
        next_hop = (
            db.query(Node)
            .filter(Node.node_id == data.next_hop)
            .first()
        )
        if next_hop is None:
            raise HTTPException(status_code=404, detail="Next-hop node not found.")

    route_status = data.status.strip().upper()
    if route_status not in {"ACTIVE", "STANDBY", "INACTIVE"}:
        raise HTTPException(
            status_code=422,
            detail="Route status must be ACTIVE, STANDBY, or INACTIVE.",
        )

    existing = (
        db.query(Route)
        .filter(
            Route.source == data.source,
            Route.destination == data.destination,
            Route.next_hop == data.next_hop,
            Route.status == route_status,
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="This route already exists with the requested status.",
        )

    route = Route(
        source=data.source,
        destination=data.destination,
        next_hop=data.next_hop,
        hop_count=data.hop_count,
        quality=data.quality,
        status=route_status,
    )

    db.add(route)
    db.add(
        Log(
            node_id=data.source,
            event_type="ROUTE_CREATED",
            description=(
                f"Route from {data.source} to {data.destination} "
                f"created by {current_user.username}."
            ),
        )
    )

    db.commit()
    db.refresh(route)
    return route


@router.get("", response_model=list[RouteResponse])
def get_routes(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Route)
        .order_by(Route.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )