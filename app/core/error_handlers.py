from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.schemas.base import ErrorResponse
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)


def create_error_response(
    message: str,
    status_code: int,
    error_code: str = None,
    details: dict = None
) -> JSONResponse:
    """Create a standardized error response."""
    error_response = ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        details=details
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    return create_error_response(
        message=exc.message,
        status_code=exc.status_code,
        error_code=exc.error_code,
        details=exc.details
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        message="Validation error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        details={"errors": errors}
    )


async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    """Handle Pydantic model validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        message="Model validation error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="MODEL_VALIDATION_ERROR",
        details={"errors": errors}
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")
    
    # Try to extract meaningful error information
    error_message = str(exc.orig) if exc.orig else "Database integrity constraint violated"
    
    return create_error_response(
        message="Database constraint violation",
        status_code=status.HTTP_409_CONFLICT,
        error_code="INTEGRITY_ERROR",
        details={"original_error": error_message}
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle general SQLAlchemy errors."""
    logger.error(f"Database error: {exc}")
    
    return create_error_response(
        message="Database error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="DATABASE_ERROR",
        details={"original_error": str(exc)}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return create_error_response(
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        details={"original_error": str(exc)} if str(exc) else None
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    
    # Register custom exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, general_exception_handler) 