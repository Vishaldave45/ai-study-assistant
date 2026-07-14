"""
Authentication token schemas.
"""

from app.schemas.base import BaseSchema


class TokenResponse(BaseSchema):
    """
    Returned after successful authentication.
    """

    access_token: str

    refresh_token: str

    token_type: str = "Bearer"
