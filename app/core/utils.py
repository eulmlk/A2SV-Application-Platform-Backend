from typing import Optional, Dict, Any
from app.core.exceptions import (
    NotFoundError, 
    UnauthorizedError, 
    ForbiddenError, 
    ConflictError, 
    ValidationError,
    InternalServerError
)


def raise_not_found(message: str, resource_type: Optional[str] = None):
    """Raise a not found exception."""
    raise NotFoundError(message, resource_type)


def raise_unauthorized(message: str = "Unauthorized access"):
    """Raise an unauthorized exception."""
    raise UnauthorizedError(message)


def raise_forbidden(message: str = "Access forbidden"):
    """Raise a forbidden exception."""
    raise ForbiddenError(message)


def raise_conflict(message: str, details: Optional[Dict[str, Any]] = None):
    """Raise a conflict exception."""
    raise ConflictError(message, details)


def raise_validation_error(message: str, details: Optional[Dict[str, Any]] = None):
    """Raise a validation error exception."""
    raise ValidationError(message, details)


def raise_internal_error(message: str = "Internal server error"):
    """Raise an internal server error exception."""
    raise InternalServerError(message)


def safe_get_attr(obj, attr_name: str, default=None):
    """Safely get an attribute from an object."""
    return getattr(obj, attr_name, default)


def safe_get_dict(dictionary: dict, key: str, default=None):
    """Safely get a value from a dictionary."""
    return dictionary.get(key, default) 