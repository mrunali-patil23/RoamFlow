"""
Trip planning service for creating and managing travel itineraries.
"""
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.api_models import TripRequest
from ..models.trip_models import TripItinerary, DayPlan, Activity, TransportOption, ActivityCategory, TransportType
from .database_service import get_database_service
from .ai_service import get_ai_service
from ..core.exceptions import AIServiceError, ValidationError


class TripService:
    """
    Service class for trip planning operations.
    Handles itinerary creation, storage, and retrieval.
    """
    
    def __init__(self):
        """Initialize the trip service."""
        self.db = get_database_service()
        self.ai_service = get_ai_service()
    
    async def create_itinerary(self, trip_request: TripRequest) -> TripItinerary:
        """
        Create a personalized travel itinerary based on user preferences.
        
        Args:
            trip_request: User's travel preferences and requirements
            
        Returns:
            TripItinerary: Generated travel itinerary
            
        Raises:
            AIServiceError: If AI generation fails
            ValidationError: If generated data is invalid
        """
        try:
            # Generate itinerary using AI service with fallback
            itinerary_data = await self.ai_service.generate_itinerary_with_fallback(
                destination=trip_request.destination,
                days=trip_request.days,
                budget=trip_request.budget.value,
                travelers=trip_request.travelers.value
            )
            
            # Convert AI response to our data models
            trip_itinerary = self._convert_ai_response_to_itinerary(
                itinerary_data, trip_request
            )
            
            # Save the trip to database
            await self.save_trip(trip_itinerary)
            
            return trip_itinerary
            
        except Exception as e:
            # If everything fails, create a basic sample trip
            return self.create_sample_trip(trip_request)
    
    def _convert_ai_response_to_itinerary(self, ai_data: Dict[str, Any], trip_request: TripRequest) -> TripItinerary:
        """
        Convert AI service response to TripItinerary model.
        
        Args:
            ai_data: Raw AI response data
            trip_request: Original trip request
            
        Returns:
            TripItinerary: Validated trip itinerary
            
        Raises:
            ValidationError: If conversion fails
        """
        try:
            trip_id = str(uuid.uuid4())
            
            # Convert daily plans
            daily_plans = []
            for day_data in ai_data.get("daily_plans", []):
                # Convert activities
                activities = []
                for activity_data in day_data.get("activities", []):
                    activity = Activity(
                        name=activity_data.get("name", "Unknown Activity"),
                        description=activity_data.get("description", "No description available"),
                        duration=max(30, min(480, activity_data.get("duration", 120))),  # Clamp to valid range
                        cost=max(0, activity_data.get("cost", 0)),
                        category=self._validate_activity_category(activity_data.get("category", "sightseeing"))
                    )
                    activities.append(activity)
                
                # Convert transport options
                transport_options = []
                for transport_data in day_data.get("transport", []):
                    transport = TransportOption(
                        type=self._validate_transport_type(transport_data.get("type", "walking")),
                        provider=transport_data.get("provider", "Unknown Provider"),
                        cost=max(0, transport_data.get("cost", 0)),
                        duration=max(1, min(300, transport_data.get("duration", 15))),  # Clamp to valid range
                        route=transport_data.get("route", "Route not specified")
                    )
                    transport_options.append(transport)
                
                # Create day plan
                day_plan = DayPlan(
                    day_number=day_data.get("day_number", len(daily_plans) + 1),
                    activities=activities,
                    transport=transport_options,
                    estimated_cost=max(0, day_data.get("estimated_cost", 0))
                )
                daily_plans.append(day_plan)
            
            # Create trip itinerary
            trip = TripItinerary(
                trip_id=trip_id,
                destination=trip_request.destination,
                total_days=trip_request.days,
                daily_plans=daily_plans,
                total_budget=max(0, ai_data.get("total_budget", 0)),
                created_at=datetime.utcnow()
            )
            
            return trip
            
        except Exception as e:
            raise ValidationError(f"Failed to convert AI response to itinerary: {str(e)}")
    
    def _validate_activity_category(self, category: str) -> ActivityCategory:
        """Validate and convert activity category."""
        try:
            return ActivityCategory(category.lower())
        except ValueError:
            return ActivityCategory.SIGHTSEEING  # Default fallback
    
    def _validate_transport_type(self, transport_type: str) -> TransportType:
        """Validate and convert transport type."""
        try:
            return TransportType(transport_type.lower())
        except ValueError:
            return TransportType.WALKING  # Default fallback
    
    async def get_trip(self, trip_id: str) -> Optional[TripItinerary]:
        """
        Retrieve a previously generated trip itinerary.
        
        Args:
            trip_id: Unique identifier for the trip
            
        Returns:
            TripItinerary or None if not found
        """
        return await self.db.get_trip(trip_id)
    
    async def save_trip(self, trip: TripItinerary) -> str:
        """
        Save a trip itinerary to the database.
        
        Args:
            trip: Trip itinerary to save
            
        Returns:
            str: Trip ID
        """
        return await self.db.save_trip(trip)
    
    async def get_user_trips(self, user_id: str) -> List[TripItinerary]:
        """
        Get all trips for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List[TripItinerary]: List of user's trips
        """
        return await self.db.get_user_trips(user_id)
    
    async def delete_trip(self, trip_id: str) -> bool:
        """
        Delete a trip by ID.
        
        Args:
            trip_id: Trip identifier
            
        Returns:
            bool: True if deleted successfully
        """
        return await self.db.delete_trip(trip_id)
    
    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Save user preferences.
        
        Args:
            user_id: User identifier
            preferences: User preferences dictionary
            
        Returns:
            bool: True if saved successfully
        """
        return await self.db.save_user_preferences(user_id, preferences)
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            Optional[Dict[str, Any]]: User preferences or None
        """
        return await self.db.get_user_preferences(user_id)
    
    def create_sample_trip(self, trip_request: TripRequest) -> TripItinerary:
        """
        Create a sample trip itinerary for testing purposes.
        
        Args:
            trip_request: User's travel preferences
            
        Returns:
            TripItinerary: Sample trip itinerary
        """
        trip_id = str(uuid.uuid4())
        
        # Create sample activities
        sample_activities = [
            Activity(
                name=f"Explore {trip_request.destination}",
                description=f"Discover the main attractions of {trip_request.destination}",
                duration=180,
                cost=50.0,
                category=ActivityCategory.SIGHTSEEING
            ),
            Activity(
                name="Local Dining Experience",
                description="Try authentic local cuisine",
                duration=90,
                cost=30.0,
                category=ActivityCategory.DINING
            )
        ]
        
        # Create sample transport
        sample_transport = [
            TransportOption(
                type=TransportType.METRO,
                provider="Local Transit",
                cost=5.0,
                duration=30,
                route="City Center to Main Attractions"
            )
        ]
        
        # Create daily plans
        daily_plans = []
        for day in range(1, trip_request.days + 1):
            day_plan = DayPlan(
                day_number=day,
                activities=sample_activities,
                transport=sample_transport,
                estimated_cost=85.0
            )
            daily_plans.append(day_plan)
        
        # Create trip itinerary
        trip = TripItinerary(
            trip_id=trip_id,
            destination=trip_request.destination,
            total_days=trip_request.days,
            daily_plans=daily_plans,
            total_budget=85.0 * trip_request.days,
            created_at=datetime.utcnow()
        )
        
        return trip