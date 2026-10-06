"""
Trip persistence service for the AI Trip Planner.

This service handles saving, retrieving, and managing trip plans in the database.
It provides high-level operations for trip plan persistence and comparison.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from database import db
from models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
from models.itinerary_models import TripPlan, Itinerary, DayPlan, Activity, WeatherInfo, ActivityType
from models.cost_models import CostBreakdown, BudgetStatus, DailyCost

logger = logging.getLogger(__name__)


class TripPersistenceService:
    """Service for persisting and retrieving trip plans"""
    
    def __init__(self):
        self.db = db
    
    def save_trip_plan(self, trip_plan: TripPlan) -> Optional[str]:
        """
        Save a complete trip plan to the database.
        
        Args:
            trip_plan: TripPlan object to save
            
        Returns:
            Trip plan ID if successful, None otherwise
        """
        try:
            # Convert trip plan to database format
            trip_data = self._trip_plan_to_db_format(trip_plan)
            
            # Save to database
            result = self.db.save_trip_plan(trip_data)
            
            if result:
                logger.info(f"Trip plan saved successfully with ID: {result['id']}")
                return result['id']
            else:
                logger.error("Failed to save trip plan")
                return None
                
        except Exception as e:
            logger.error(f"Error saving trip plan: {e}")
            return None
    
    def get_saved_trips(self, user_id: str) -> List[TripPlan]:
        """
        Get all saved trip plans for a user.
        
        Args:
            user_id: User ID to get trips for
            
        Returns:
            List of TripPlan objects
        """
        try:
            trips_data = self.db.get_saved_trips(user_id)
            
            trips = []
            for trip_data in trips_data:
                trip_plan = self._db_format_to_trip_plan(trip_data)
                if trip_plan:
                    trips.append(trip_plan)
            
            logger.info(f"Retrieved {len(trips)} saved trips for user {user_id}")
            return trips
            
        except Exception as e:
            logger.error(f"Error getting saved trips: {e}")
            return []
    
    def get_trip_plan_by_id(self, trip_plan_id: str, user_id: str = None) -> Optional[TripPlan]:
        """
        Get a specific trip plan by ID.
        
        Args:
            trip_plan_id: Trip plan ID
            user_id: Optional user ID for ownership verification
            
        Returns:
            TripPlan object if found, None otherwise
        """
        try:
            trip_data = self.db.get_trip_plan_by_id(trip_plan_id, user_id)
            
            if trip_data:
                trip_plan = self._db_format_to_trip_plan(trip_data)
                logger.info(f"Retrieved trip plan {trip_plan_id}")
                return trip_plan
            else:
                logger.warning(f"Trip plan {trip_plan_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting trip plan by ID: {e}")
            return None
    
    def delete_trip_plan(self, trip_plan_id: str, user_id: str) -> bool:
        """
        Delete a trip plan (only by the owner).
        
        Args:
            trip_plan_id: Trip plan ID to delete
            user_id: User ID for ownership verification
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            success = self.db.delete_trip_plan(trip_plan_id, user_id)
            
            if success:
                logger.info(f"Trip plan {trip_plan_id} deleted successfully")
            else:
                logger.warning(f"Failed to delete trip plan {trip_plan_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting trip plan: {e}")
            return False
    
    def compare_trip_plans(self, trip_plan_ids: List[str], user_id: str) -> List[TripPlan]:
        """
        Get multiple trip plans for comparison.
        
        Args:
            trip_plan_ids: List of trip plan IDs to compare
            user_id: User ID for ownership verification
            
        Returns:
            List of TripPlan objects for comparison
        """
        try:
            trips_data = self.db.compare_trip_plans(trip_plan_ids, user_id)
            
            trips = []
            for trip_data in trips_data:
                trip_plan = self._db_format_to_trip_plan(trip_data)
                if trip_plan:
                    trips.append(trip_plan)
            
            logger.info(f"Retrieved {len(trips)} trip plans for comparison")
            return trips
            
        except Exception as e:
            logger.error(f"Error comparing trip plans: {e}")
            return []
    
    def _trip_plan_to_db_format(self, trip_plan: TripPlan) -> Dict[str, Any]:
        """Convert TripPlan object to database format"""
        
        # Convert preferences
        preferences = trip_plan.preferences
        
        # Convert itinerary days
        itinerary_days = []
        for day in trip_plan.itinerary.days:
            activities_json = []
            for activity in day.activities:
                activity_dict = {
                    "name": activity.name,
                    "activity_type": activity.activity_type.value,
                    "description": activity.description,
                    "duration_hours": activity.duration_hours,
                    "cost_inr": activity.cost_inr,
                    "location": activity.location,
                    "rating": activity.rating,
                    "start_time": activity.start_time,
                    "end_time": activity.end_time,
                    "booking_required": activity.booking_required,
                    "source_data": activity.source_data
                }
                activities_json.append(activity_dict)
            
            weather_json = {
                "date": day.weather.date.isoformat(),
                "temperature_high": day.weather.temperature_high,
                "temperature_low": day.weather.temperature_low,
                "condition": day.weather.condition,
                "description": day.weather.description,
                "humidity": day.weather.humidity,
                "precipitation_chance": day.weather.precipitation_chance
            }
            
            itinerary_days.append({
                "day_number": day.day_number,
                "date": day.date.isoformat(),
                "activities": activities_json,
                "weather_info": weather_json,
                "daily_cost_inr": day.daily_cost_inr
            })
        
        # Convert cost breakdown
        cost_breakdown = {
            "flight_cost_inr": trip_plan.cost_breakdown.flight_cost_inr,
            "hotel_cost_inr": trip_plan.cost_breakdown.hotel_cost_inr,
            "attractions_cost_inr": trip_plan.cost_breakdown.attractions_cost_inr,
            "events_cost_inr": trip_plan.cost_breakdown.events_cost_inr,
            "local_expenses_inr": trip_plan.cost_breakdown.local_expenses_inr
        }
        
        return {
            "user_id": trip_plan.user_id,
            "destination": preferences.destination,
            "start_date": preferences.start_date.isoformat(),
            "end_date": preferences.end_date.isoformat(),
            "travel_days": preferences.travel_days,
            "travel_type": preferences.travel_type.value,
            "budget_preference": preferences.budget_preference.value,
            "max_budget_inr": preferences.max_budget_inr,
            "interests": [interest.value for interest in preferences.interests],
            "total_cost_inr": trip_plan.cost_breakdown.total_cost_inr,
            "budget_status": trip_plan.budget_status.status,
            "itinerary_days": itinerary_days,
            "cost_breakdown": cost_breakdown
        }
    
    def _db_format_to_trip_plan(self, trip_data: Dict[str, Any]) -> Optional[TripPlan]:
        """Convert database format to TripPlan object"""
        try:
            from datetime import datetime, date
            
            # Convert preferences
            preferences = TripPreferences(
                destination=trip_data["destination"],
                start_date=datetime.fromisoformat(trip_data["start_date"]).date(),
                end_date=datetime.fromisoformat(trip_data["end_date"]).date(),
                travel_days=trip_data["travel_days"],
                travel_type=TravelType(trip_data["travel_type"]),
                budget_preference=BudgetLevel(trip_data["budget_preference"]),
                max_budget_inr=float(trip_data["max_budget_inr"]),
                interests=[Interest(interest) for interest in trip_data["interests"]]
            )
            
            # Convert itinerary days
            days = []
            for day_data in trip_data.get("itinerary_days", []):
                activities = []
                for activity_data in day_data["activities"]:
                    activity = Activity(
                        name=activity_data["name"],
                        activity_type=ActivityType(activity_data["activity_type"]),
                        description=activity_data["description"],
                        duration_hours=activity_data["duration_hours"],
                        cost_inr=activity_data["cost_inr"],
                        location=activity_data.get("location", ""),
                        rating=activity_data.get("rating"),
                        start_time=activity_data.get("start_time"),
                        end_time=activity_data.get("end_time"),
                        booking_required=activity_data.get("booking_required", False),
                        source_data=activity_data.get("source_data")
                    )
                    activities.append(activity)
                
                weather_data = day_data["weather_info"]
                weather = WeatherInfo(
                    date=datetime.fromisoformat(weather_data["date"]).date(),
                    temperature_high=weather_data.get("temperature_high"),
                    temperature_low=weather_data.get("temperature_low"),
                    condition=weather_data.get("condition", "Unknown"),
                    description=weather_data.get("description", ""),
                    humidity=weather_data.get("humidity"),
                    precipitation_chance=weather_data.get("precipitation_chance")
                )
                
                day_plan = DayPlan(
                    day_number=day_data["day_number"],
                    date=datetime.fromisoformat(day_data["date"]).date(),
                    activities=activities,
                    weather=weather,
                    daily_cost_inr=day_data["daily_cost_inr"]
                )
                days.append(day_plan)
            
            # Create itinerary
            itinerary = Itinerary(
                trip_id=trip_data["id"],
                days=days,
                total_cost_inr=float(trip_data["total_cost_inr"]),
                created_at=trip_data.get("created_at")
            )
            
            # Convert cost breakdown
            cost_data = trip_data.get("cost_breakdown", {})
            cost_breakdown = CostBreakdown(
                flight_cost_inr=float(cost_data.get("flight_cost_inr", 0)),
                hotel_cost_inr=float(cost_data.get("hotel_cost_inr", 0)),
                attractions_cost_inr=float(cost_data.get("attractions_cost_inr", 0)),
                events_cost_inr=float(cost_data.get("events_cost_inr", 0)),
                local_expenses_inr=float(cost_data.get("local_expenses_inr", 0)),
                total_cost_inr=float(trip_data["total_cost_inr"]),
                daily_breakdown=[]  # Could be populated from itinerary days if needed
            )
            
            # Create budget status
            budget_status = BudgetStatus.calculate_status(
                total_cost_inr=float(trip_data["total_cost_inr"]),
                max_budget_inr=preferences.max_budget_inr
            )
            
            # Create trip plan
            trip_plan = TripPlan(
                id=trip_data["id"],
                user_id=trip_data["user_id"],
                preferences=preferences,
                itinerary=itinerary,
                cost_breakdown=cost_breakdown,
                budget_status=budget_status,
                created_at=trip_data.get("created_at"),
                updated_at=trip_data.get("updated_at")
            )
            
            return trip_plan
            
        except Exception as e:
            logger.error(f"Error converting database format to trip plan: {e}")
            return None


# Global service instance
trip_persistence_service = TripPersistenceService()