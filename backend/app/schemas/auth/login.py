"""
Authentication schemas for user login.
"""

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    """
    Request schema for login.
    """

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )
