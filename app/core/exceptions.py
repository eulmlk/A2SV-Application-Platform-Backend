from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class AppException(HTTPException):
    """Base custom exception for the application."""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ValidationError(AppException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(AppException):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        details = {"resource_type": resource_type} if resource_type else None
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            error_code="NOT_FOUND",
            details=details
        )


class UnauthorizedError(AppException):
    """Exception for unauthorized access errors."""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(AppException):
    """Exception for forbidden access errors."""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code="FORBIDDEN"
        )


class ConflictError(AppException):
    """Exception for resource conflict errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code="CONFLICT",
            details=details
        )


class InternalServerError(AppException):
    """Exception for internal server errors."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            error_code="INTERNAL_SERVER_ERROR"
        ) 