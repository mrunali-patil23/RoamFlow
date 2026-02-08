"""
Health check endpoints for API monitoring and status verification.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from ....core.dependencies import get_health_service

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns API status and service information.
    """
    return {
        "status": "healthy",
        "service": "ai-travel-planner-api",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(
    health_service=Depends(get_health_service)
) -> Dict[str, Any]:
    """
    Detailed health check including external service status.
    """
    return await health_service.get_detailed_status()