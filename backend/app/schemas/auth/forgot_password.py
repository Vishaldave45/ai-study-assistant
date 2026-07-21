from pydantic import EmailStr
from app.schemas.base import BaseSchema


class ForgotPasswordRequest(BaseSchema):
    email: EmailStr
