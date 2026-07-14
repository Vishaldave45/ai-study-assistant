"""
Authentication schemas for user registration.
"""

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class RegisterRequest(BaseSchema):
    """
    Request schema for user registration.
    """

    email: EmailStr

    full_name: str = Field(
        min_length=2,
        max_length=255,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class RegisterResponse(BaseSchema):
    """
    Response returned after successful registration.
    """

    message: str
