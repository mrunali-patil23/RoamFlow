"""
Global exception handlers for the FastAPI application.
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from .exceptions import TravelPlannerException
from ..models.api_models import ErrorResponse

logger = logging.getLogger(__name__)

async def travel_planner_exception_handler(
    request: Request, 
    exc: TravelPlannerException
) -> JSONResponse:
    """
    Handle custom TravelPlannerException instances.
    """
    logger.error(f"TravelPlannerException: {exc.message}", extra={
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "details": exc.details,
        "path": request.url.path,
        "method": request.method
    })
    
    error_response = ErrorResponse(
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        retry_after=exc.details.get("retry_after") if exc.details else None
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException instances.
    """
    logger.warning(f"HTTPException: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method
    })
    
    error_response = ErrorResponse(
        message=str(exc.detail),
        error_code="HTTP_ERROR",
        details={"status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    """
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "method": request.method,
        "errors": exc.errors()
    })
    
    # Format validation errors for better user experience
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        message="Request validation failed",
        error_code="VALIDATION_ERROR",
        details={"validation_errors": formatted_errors}
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.
    """
    logger.error(f"Unexpected error: {str(exc)}", extra={
        "path": request.url.path,
        "method": request.method,
        "exception_type": type(exc).__name__
    }, exc_info=True)
    
    error_response = ErrorResponse(
        message="An unexpected error occurred. Please try again later.",
        error_code="INTERNAL_SERVER_ERROR",
        details={"exception_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )