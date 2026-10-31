
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserManagementSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserAdminCreate(UserManagementSchema):
    name: str = Field(min_length=2, max_length=120)

    username: str = Field(
        min_length=3,
        max_length=80,
        pattern=r"^[A-Za-z0-9_.-]+$",
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    role: str = Field(
        default="OPERATOR",
        min_length=3,
        max_length=20,
    )


class UserAdminUpdate(UserManagementSchema):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    role: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=20,
    )


class UserStatusUpdate(UserManagementSchema):
    is_active: bool


class UserPasswordReset(UserManagementSchema):
    password: str = Field(
        min_length=8,
        max_length=72,
    )


class UserAdminResponse(UserManagementSchema):
    user_id: int
    name: str
    role: str
    username: str
    is_active: bool
    created_at: datetime
