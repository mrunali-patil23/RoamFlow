"""
Custom exception classes for the AI Travel Planner API.
"""
from typing import Any, Dict, Optional

class TravelPlannerException(Exception):
    """Base exception class for travel planner errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(TravelPlannerException):
    """Exception for input validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )

class ExternalServiceError(TravelPlannerException):
    """Exception for external service failures."""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service_name} service error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=503,
            details=details
        )

class NotFoundError(TravelPlannerException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            error_code="NOT_FOUND",
            status_code=404
        )

class RateLimitError(TravelPlannerException):
    """Exception for rate limiting errors."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after}
        )

class AIServiceError(TravelPlannerException):
    """Exception for AI service errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"AI service error: {message}",
            error_code="AI_SERVICE_ERROR",
            status_code=503,
            details=details
        )