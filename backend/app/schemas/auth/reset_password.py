from pydantic import Field
from app.schemas.base import BaseSchema


class ResetPasswordRequest(BaseSchema):
    token: str
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The new password to set."
    )
