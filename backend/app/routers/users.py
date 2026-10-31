
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_admin
from ..models import User, Log
from ..schemas import UserResponse
from ..security import hash_password
from ..user_schemas import (
    UserAdminCreate,
    UserAdminUpdate,
    UserAdminResponse,
    UserStatusUpdate,
    UserPasswordReset,
)


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)

VALID_ROLES = {"ADMIN", "OPERATOR", "VIEWER"}


def get_active_admin_count(db: Session) -> int:
    return (
        db.query(User)
        .filter(
            User.role == "ADMIN",
            User.is_active.is_(True),
        )
        .count()
    )


def add_user_audit(
    db: Session,
    event_type: str,
    description: str,
):
    db.add(
        Log(
            node_id=None,
            event_type=event_type,
            description=description,
        )
    )


def check_password_length(password: str):
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=422,
            detail="Password cannot exceed 72 UTF-8 bytes.",
        )


def find_user_or_404(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return user


# =========================================================
# CURRENT USER PROFILE
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


# =========================================================
# LIST ALL USERS
# =========================================================

@router.get(
    "",
    response_model=list[UserAdminResponse],
)
def get_all_users(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return (
        db.query(User)
        .order_by(User.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# =========================================================
# CREATE USER
# =========================================================

@router.post(
    "",
    response_model=UserAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    username = data.username.strip().lower()
    role = data.role.strip().upper()
    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Name cannot be empty.",
        )

    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=422,
            detail=f"Role must be one of {sorted(VALID_ROLES)}.",
        )

    check_password_length(data.password)

    existing = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="A user with this username already exists.",
        )

    user = User(
        name=name,
        username=username,
        role=role,
        password_hash=hash_password(data.password),
        is_active=True,
        token_version=0,
    )

    db.add(user)
    db.flush()

    add_user_audit(
        db,
        "USER_CREATED",
        (
            f"User '{username}' created with role {role} "
            f"by administrator '{current_user.username}'."
        ),
    )

    db.commit()
    db.refresh(user)

    return user


# =========================================================
# GET ONE USER
# =========================================================

@router.get(
    "/{user_id}",
    response_model=UserAdminResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return find_user_or_404(db, user_id)


# =========================================================
# UPDATE USER NAME OR ROLE
# =========================================================

@router.put(
    "/{user_id}",
    response_model=UserAdminResponse,
)
def update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = find_user_or_404(db, user_id)

    if not data.model_fields_set:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one field to update.",
        )

    changes = []
    role_changed = False

    if "name" in data.model_fields_set:
        if data.name is None or not data.name.strip():
            raise HTTPException(
                status_code=422,
                detail="Name cannot be empty.",
            )

        user.name = data.name.strip()
        changes.append("name updated")

    if "role" in data.model_fields_set:
        if data.role is None:
            raise HTTPException(
                status_code=422,
                detail="Role cannot be empty.",
            )

        new_role = data.role.strip().upper()

        if new_role not in VALID_ROLES:
            raise HTTPException(
                status_code=422,
                detail=f"Role must be one of {sorted(VALID_ROLES)}.",
            )

        if user.role != new_role:

            if user.user_id == current_user.user_id:
                raise HTTPException(
                    status_code=409,
                    detail="Administrators cannot change their own role.",
                )

            if (
                user.is_active
                and user.role == "ADMIN"
                and new_role != "ADMIN"
                and get_active_admin_count(db) <= 1
            ):
                raise HTTPException(
                    status_code=409,
                    detail="The last active administrator cannot be demoted.",
                )

            user.role = new_role
            user.token_version += 1
            role_changed = True
            changes.append(f"role changed to {new_role}")

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="No changes were supplied.",
        )

    add_user_audit(
        db,
        "USER_UPDATED",
        (
            f"User '{user.username}' updated: {', '.join(changes)} "
            f"by administrator '{current_user.username}'."
        ),
    )

    db.commit()
    db.refresh(user)

    return user


# =========================================================
# ACTIVATE OR DEACTIVATE USER
# =========================================================

@router.patch(
    "/{user_id}/status",
    response_model=UserAdminResponse,
)
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = find_user_or_404(db, user_id)

    if user.user_id == current_user.user_id and not data.is_active:
        raise HTTPException(
            status_code=409,
            detail="You cannot deactivate your own administrator account.",
        )

    if user.is_active == data.is_active:
        return user

    if (
        not data.is_active
        and user.role == "ADMIN"
        and get_active_admin_count(db) <= 1
    ):
        raise HTTPException(
            status_code=409,
            detail="The last active administrator cannot be deactivated.",
        )

    user.is_active = data.is_active

    # Revoke all previously issued tokens for this account.
    user.token_version += 1

    event_type = (
        "USER_ACTIVATED"
        if data.is_active
        else "USER_DEACTIVATED"
    )

    add_user_audit(
        db,
        event_type,
        (
            f"User '{user.username}' was "
            f"{'activated' if data.is_active else 'deactivated'} "
            f"by administrator '{current_user.username}'."
        ),
    )

    db.commit()
    db.refresh(user)

    return user


# =========================================================
# ADMIN PASSWORD RESET
# =========================================================

@router.patch(
    "/{user_id}/password",
    response_model=UserAdminResponse,
)
def reset_user_password(
    user_id: int,
    data: UserPasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = find_user_or_404(db, user_id)

    check_password_length(data.password)

    user.password_hash = hash_password(data.password)

    # Old JWTs will no longer be accepted.
    user.token_version += 1

    add_user_audit(
        db,
        "USER_PASSWORD_RESET",
        (
            f"Password reset for user '{user.username}' "
            f"by administrator '{current_user.username}'."
        ),
    )

    db.commit()
    db.refresh(user)

    return user
