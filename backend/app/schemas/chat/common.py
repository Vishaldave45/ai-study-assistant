from pydantic import Field
from app.schemas.base import BaseSchema


class TokenUsage(BaseSchema):
    """
    Schema for tracking AI token usage.
    """
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the generated completion")
    total_tokens: int = Field(..., description="Total number of tokens used in the request")


class ErrorResponse(BaseSchema):
    """
    Standard schema for error responses.
    """
    detail: str = Field(..., description="Detailed message describing the error")


class SuccessResponse(BaseSchema):
    """
    Standard schema for simple successful operations.
    """
    message: str = Field(..., description="Information message indicating success")


class BasePagination(BaseSchema):
    """
    Base schema for paginated responses.
    """
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total number of items across all pages")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
