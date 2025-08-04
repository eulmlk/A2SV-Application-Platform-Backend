# app/core/schemas/base.py

from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

# This creates a generic TypeVar. It can be any type.
T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    A generic API response wrapper.

    This provides a consistent structure for all API responses.
    """

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    A standardized error response wrapper.
    """
    success: bool = False
    data: Optional[dict] = None
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
