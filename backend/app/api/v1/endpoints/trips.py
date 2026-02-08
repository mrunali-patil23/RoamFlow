"""
Trip planning endpoints for creating and managing travel itineraries.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ....models.api_models import TripRequest, TripResponse
from ....core.dependencies import get_trip_service

router = APIRouter()

@router.post("/plan-trip", response_model=TripResponse)
async def plan_trip(
    trip_request: TripRequest,
    trip_service=Depends(get_trip_service)
) -> TripResponse:
    """
    Create a personalized travel itinerary based on user preferences.
    
    Requirements: 6.1 - POST /plan-trip endpoint
    """
    try:
        itinerary = await trip_service.create_itinerary(trip_request)
        return TripResponse(
            success=True,
            data=itinerary,
            message="Trip itinerary generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trip itinerary: {str(e)}"
        )

@router.get("/trip/{trip_id}")
async def get_trip(
    trip_id: str,
    trip_service=Depends(get_trip_service)
) -> TripResponse:
    """
    Retrieve a previously generated trip itinerary.
    """
    try:
        trip = await trip_service.get_trip(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        return TripResponse(
            success=True,
            data=trip,
            message="Trip retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve trip: {str(e)}"
        )