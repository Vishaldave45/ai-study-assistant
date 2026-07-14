"""
User response schemas.
"""

from datetime import datetime
from uuid import UUID

from app.database.enums import UserStatus
from app.schemas.base import BaseSchema


class UserResponse(BaseSchema):
    """
    Public user representation.
    """

    id: UUID

    email: str

    full_name: str

    status: UserStatus

    is_verified: bool

    created_at: datetime
