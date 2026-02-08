"""
Transport endpoints for flight and local transport information.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import date
from ....models.api_models import FlightSearchParams, TransportRequest, TransportResponse
from ....core.dependencies import get_transport_service

router = APIRouter()

@router.get("/flights", response_model=TransportResponse)
async def get_flights(
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
    try:
        flight_params = FlightSearchParams(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers
        )
        
        flights = await transport_service.search_flights(flight_params)
        return TransportResponse(
            success=True,
            data=flights,
            message="Flight options retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve flight options: {str(e)}"
        )

@router.get("/local-transport", response_model=TransportResponse)
async def get_local_transport(
    location: str = Query(..., description="City or location name"),
    transport_type: Optional[str] = Query(None, description="Specific transport type (taxi, bus, metro)"),
    transport_service=Depends(get_transport_service)
) -> TransportResponse:
    """
    Get local transport options and cost estimates for a location.
    
    Requirements: 6.3 - GET /local-transport endpoint
    """
    try:
        transport_request = TransportRequest(
            location=location,
            transport_type=transport_type
        )
        
        transport_options = await transport_service.get_local_transport(transport_request)
        return TransportResponse(
            success=True,
            data=transport_options,
            message="Local transport options retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve local transport options: {str(e)}"
        )