"""
Main API v1 router that aggregates all route modules.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from .endpoints import trips, transport, health

# Create main API v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_router.include_router(transport.router, prefix="/transport", tags=["transport"])

# Add the main endpoints directly to the main router as per requirements 6.1, 6.2, 6.3
from .endpoints.trips import plan_trip
from .endpoints.transport import get_flights, get_local_transport
from ...core.dependencies import get_trip_service, get_transport_service
from ...models.api_models import TripRequest, TripResponse, TransportResponse

@api_router.post("/plan-trip", response_model=TripResponse, tags=["trips"])
async def plan_trip_endpoint(
    trip_request: TripRequest,
    trip_service=Depends(get_trip_service)
) -> TripResponse:
    """
    Create a personalized travel itinerary based on user preferences.
    
    Requirements: 6.1 - POST /plan-trip endpoint
    """
    return await plan_trip(trip_request, trip_service)

@api_router.get("/flights", response_model=TransportResponse, tags=["transport"])
async def flights_endpoint(
    origin: str = Query(..., description="Origin airport code or city"),
    destination: str = Query(..., description="Destination airport code or city"),
    departure_date: date = Query(..., description="Departure date"),
    return_date: Optional[date] = Query(None, description="Return date for round trip"),
    passengers: int = Query(1, ge=1, le=9, description="Number of passengers"),
    transport_service=Depends(get_transport_service)
) -> TransportResponse:
    """
    Get real-time flight options for specified route and dates.
    
    Requirements: 6.2 - GET /flights endpoint
    """
    return await get_flights(origin, destination, departure_date, return_date, passengers, transport_service)

@api_router.get("/local-transport", response_model=TransportResponse, tags=["transport"])
async def local_transport_endpoint(
    location: str = Query(..., description="City or location name"),
    transport_type: Optional[str] = Query(None, description="Specific transport type (taxi, bus, metro)"),
    transport_service=Depends(get_transport_service)
) -> TransportResponse:
    """
    Get local transport options and cost estimates for a location.
    
    Requirements: 6.3 - GET /local-transport endpoint
    """
    return await get_local_transport(location, transport_type, transport_service)