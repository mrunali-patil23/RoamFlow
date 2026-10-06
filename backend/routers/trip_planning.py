"""
Trip Planning API Router
Handles trip planning, itinerary generation, and trip management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging
from dataclasses import asdict

from routers.auth import get_current_user_dependency
from services.trip_planning_service import TripPlanningService
from models.trip_preferences import TripPreferences

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trip-planning", tags=["trip-planning"])

# Initialize services
trip_service = TripPlanningService()


@router.post("/create")
async def create_trip_plan(
    preferences: TripPreferences,
    current_user: dict = Depends(get_current_user_dependency)
) -> Dict[str, Any]:
    """
    Create a complete trip plan with itinerary and cost breakdown.
    
    Args:
        preferences: Trip preferences from the user
        current_user: Authenticated user
        
    Returns:
        Dict: Complete trip plan with itinerary and costs
    """
    try:
        logger.info(f"Creating trip plan for user {current_user['id']}")
        
        # Create trip plan
        trip_plan = trip_service.create_trip_plan(preferences)
        
        # Convert to dict for JSON serialization
        trip_plan_dict = {
            "id": trip_plan.id,
            "user_id": str(current_user["id"]),
            "preferences": asdict(preferences),
            "itinerary": {
                "trip_id": trip_plan.itinerary.trip_id,
                "days": [
                    {
                        "day_number": day.day_number,
                        "date": day.date.isoformat(),
                        "activities": [
                            {
                                "name": activity.name,
                                "description": activity.description,
                                "activity_type": activity.activity_type.value,
                                "cost_inr": activity.cost_inr,
                                "duration_hours": activity.duration_hours,
                                "rating": activity.rating,
                                "location": activity.location,
                                "start_time": activity.start_time,
                                "end_time": activity.end_time,
                                "booking_required": activity.booking_required
                            } for activity in day.activities
                        ],
                        "weather": {
                            "date": day.weather.date.isoformat(),
                            "condition": day.weather.condition,
                            "temperature_high": day.weather.temperature_high,
                            "temperature_low": day.weather.temperature_low
                        } if day.weather else None,
                        "daily_cost_inr": day.daily_cost_inr
                    } for day in trip_plan.itinerary.days
                ],
                "total_cost_inr": trip_plan.itinerary.total_cost_inr
            },
            "cost_breakdown": {
                "flight_cost_inr": trip_plan.cost_breakdown.flight_cost_inr,
                "hotel_cost_inr": trip_plan.cost_breakdown.hotel_cost_inr,
                "attractions_cost_inr": trip_plan.cost_breakdown.attractions_cost_inr,
                "events_cost_inr": trip_plan.cost_breakdown.events_cost_inr,
                "local_expenses_inr": trip_plan.cost_breakdown.local_expenses_inr,
                "total_cost_inr": trip_plan.cost_breakdown.total_cost_inr
            },
            "budget_status": {
                "status": trip_plan.budget_status.status,
                "difference_inr": trip_plan.budget_status.difference_inr,
                "suggestions": trip_plan.budget_status.suggestions
            }
        }
        
        logger.info(f"Trip plan created successfully: {trip_plan.id}")
        return trip_plan_dict
        
    except Exception as e:
        logger.error(f"Error creating trip plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trip plan: {str(e)}"
        )


@router.get("/saved")
async def get_saved_trips(
    current_user: dict = Depends(get_current_user_dependency)
) -> List[Dict[str, Any]]:
    """
    Get all saved trip plans for the current user.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List[Dict]: List of saved trip plans
    """
    try:
        logger.info(f"Retrieving saved trips for user {current_user['id']}")
        
        saved_trips = trip_service.get_saved_trips(str(current_user["id"]))
        
        return []  # Return empty list for now since database persistence is not implemented
        
    except Exception as e:
        logger.error(f"Error retrieving saved trips: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve saved trips: {str(e)}"
        )


@router.get("/{trip_id}")
async def get_trip_plan(
    trip_id: str,
    current_user: dict = Depends(get_current_user_dependency)
) -> Dict[str, Any]:
    """
    Get a specific trip plan by ID.
    
    Args:
        trip_id: Trip plan identifier
        current_user: Authenticated user
        
    Returns:
        Dict: Trip plan details
    """
    try:
        logger.info(f"Retrieving trip plan {trip_id} for user {current_user['id']}")
        
        # TODO: Implement database retrieval by ID
        # For now, return a placeholder response
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip plan not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trip plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trip plan: {str(e)}"
        )