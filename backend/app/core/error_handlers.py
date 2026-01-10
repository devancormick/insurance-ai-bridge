"""Error handlers for the application."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.core.exceptions import InsuranceAIBridgeException
from app.utils.logging import logger
import traceback


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation exception
        
    Returns:
        JSON error response
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "path": str(request.url.path)
        }
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.
    
    Args:
        request: FastAPI request
        exc: SQLAlchemy exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Database error on {request.url.path}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database error",
            "message": "A database error occurred. Please try again later.",
            "path": str(request.url.path)
        }
    )


async def custom_exception_handler(
    request: Request, exc: InsuranceAIBridgeException
) -> JSONResponse:
    """
    Handle custom application exceptions.
    
    Args:
        request: FastAPI request
        exc: Custom exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Application error on {request.url.path}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": str(request.url.path)
        },
        headers=exc.headers or {}
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handle all other unhandled exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON error response
    """
    logger.error(
        f"Unhandled exception on {request.url.path}: {exc}",
        exc_info=True
    )
    
    # Don't expose internal error details in production
    detail = "Internal server error"
    if settings.debug:
        detail = str(exc)
        traceback_str = traceback.format_exc()
        logger.debug(f"Traceback: {traceback_str}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "path": str(request.url.path),
            "type": type(exc).__name__
        }
    )

