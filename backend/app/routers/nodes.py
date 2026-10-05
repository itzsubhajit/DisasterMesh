from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Node, User
from ..schemas import NodeCreate, NodeResponse, NodeStatusResponse


router = APIRouter(
    prefix="/api/nodes",
    tags=["Nodes"],
)


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
    """
    Register a new DisasterMesh field, relay, or gateway node.
    """

    existing_node_id = (
        db.query(Node)
        .filter(Node.node_id == node_data.node_id)
        .first()
    )

    if existing_node_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A node with this node_id is already registered.",
        )

    existing_device_id = (
        db.query(Node)
        .filter(Node.device_id == node_data.device_id)
        .first()
    )

    if existing_device_id is not None:
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
        status=node_data.status,
        last_seen=datetime.now(timezone.utc),
    )

    db.add(node)
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
    """
    Return all registered DisasterMesh nodes.
    """

    nodes = (
        db.query(Node)
        .order_by(Node.node_id)
        .all()
    )

    return nodes


@router.get(
    "/status",
    response_model=NodeStatusResponse,
)
def get_node_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a summary of the current DisasterMesh node health.
    """

    nodes = db.query(Node).all()

    total_nodes = len(nodes)
    online_nodes = 0
    offline_nodes = 0
    stale_nodes = 0

    current_time = datetime.now(timezone.utc)
    stale_threshold = timedelta(minutes=5)

    for node in nodes:
        if node.status.upper() == "ONLINE":
            online_nodes += 1
        else:
            offline_nodes += 1

        if node.last_seen is not None:
            last_seen = node.last_seen

            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)

            if current_time - last_seen > stale_threshold:
                stale_nodes += 1

    return NodeStatusResponse(
        total_nodes=total_nodes,
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
    """
    Return details of one registered DisasterMesh node.
    """

    node = (
        db.query(Node)
        .filter(Node.node_id == node_id)
        .first()
    )

    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node '{node_id}' was not found.",
        )

    return node