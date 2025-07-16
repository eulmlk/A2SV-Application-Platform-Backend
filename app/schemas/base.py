# app/core/schemas/base.py

from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

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
