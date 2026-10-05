from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_current_user
from ..models import User
from ..schemas import UserResponse


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Return the profile of the currently authenticated user.
    """

    return current_user