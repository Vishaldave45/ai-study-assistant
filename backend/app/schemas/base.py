"""
Base Pydantic schema.

Every request/response schema should inherit from BaseSchema.
"""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )
