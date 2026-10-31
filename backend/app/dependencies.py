
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=True)


def authentication_error(detail: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except (JWTError, ValueError, TypeError):
        raise authentication_error(
            "Invalid or expired authentication token."
        )

    if not isinstance(payload, dict):
        raise authentication_error(
            "Invalid or expired authentication token."
        )

    username = payload.get("sub")

    if not username:
        raise authentication_error(
            "Invalid authentication token."
        )

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if user is None:
        raise authentication_error(
            "Authenticated user no longer exists."
        )

    if not user.is_active:
        raise authentication_error(
            "This user account has been deactivated."
        )

    # Older development tokens without a version claim are treated
    # as version zero. The migration assigns existing users version 0.
    token_version = payload.get("ver", 0)

    if (
        isinstance(token_version, bool)
        or not isinstance(token_version, int)
        or token_version != user.token_version
    ):
        raise authentication_error(
            "This token has been revoked. Please log in again."
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges are required.",
        )

    return current_user


def require_operator_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role not in {"OPERATOR", "ADMIN"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator or administrator privileges are required.",
        )

    return current_user
