"""
Health monitoring service for API status and external service checks.
"""
from typing import Dict, Any
from app.services.ai_service import get_ai_service

class HealthService:
    """
    Service class for health monitoring and status checks.
    """
    
    def __init__(self):
        """Initialize the health service."""
        pass
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """
        Get detailed health status including external service checks.
        
        Returns:
            Dictionary containing detailed health information
        """
        # Check AI service health
        try:
            ai_service = get_ai_service()
            ai_status = await ai_service.check_health()
            gemini_status = ai_status.get("status", "unknown")
        except Exception:
            gemini_status = "error"
        
        return {
            "status": "healthy",
            "service": "ai-travel-planner-api",
            "version": "1.0.0",
            "external_services": {
                "gemini_ai": gemini_status,
                "amadeus_api": "not_checked",
                "database": "not_checked"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }