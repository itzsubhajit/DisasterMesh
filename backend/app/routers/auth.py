
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, LoginResponse
from ..security import create_access_token, verify_password


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.username == login_data.username.strip().lower())
        .first()
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(
            login_data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    access_token = create_access_token(
        subject=user.username,
        role=user.role,
        name=user.name,
        token_version=user.token_version,
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        name=user.name,
        role=user.role,
    )
