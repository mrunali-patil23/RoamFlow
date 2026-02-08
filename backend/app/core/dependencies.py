"""
Dependency injection configuration for FastAPI.
Provides service instances and manages their lifecycle.
"""
from typing import Generator
from ..services.trip_service import TripService
from ..services.transport_service import TransportService
from ..services.health_service import HealthService
from ..services.database_service import DatabaseService, get_database_service
from ..services.ai_service import AIService, get_ai_service

# Service instances (will be replaced with proper DI container in production)
_trip_service = None
_transport_service = None
_health_service = None

def get_trip_service() -> TripService:
    """
    Dependency provider for TripService.
    Returns a singleton instance of the trip planning service.
    """
    global _trip_service
    if _trip_service is None:
        _trip_service = TripService()
    return _trip_service

def get_transport_service() -> TransportService:
    """
    Dependency provider for TransportService.
    Returns a singleton instance of the transport service.
    """
    global _transport_service
    if _transport_service is None:
        _transport_service = TransportService()
    return _transport_service

def get_health_service() -> HealthService:
    """
    Dependency provider for HealthService.
    Returns a singleton instance of the health monitoring service.
    """
    global _health_service
    if _health_service is None:
        _health_service = HealthService()
    return _health_service

def get_database_service_dependency() -> DatabaseService:
    """
    Dependency provider for DatabaseService.
    Returns the singleton instance of the database service.
    """
    return get_database_service()

def get_ai_service_dependency() -> AIService:
    """
    Dependency provider for AIService.
    Returns the singleton instance of the AI service.
    """
    return get_ai_service()