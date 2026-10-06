"""
Database connection and configuration for Supabase.
Handles database initialization and connection management.
"""

from supabase import create_client, Client
from config import settings
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager for Supabase"""
    
    def __init__(self):
        self.client: Client = None
        self._initialized = False
    
    def _initialize_connection(self):
        """Initialize Supabase client connection"""
        if self._initialized:
            return
            
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("Supabase URL and Key must be provided")
            
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self._initialized = True
            logger.info("Supabase connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase connection: {e}")
            raise
    
    def _ensure_connection(self):
        """Ensure database connection is initialized"""
        if not self._initialized:
            self._initialize_connection()
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        self._ensure_connection()
        return self.client
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy"""
        self._ensure_connection()
        try:
            # Simple query to test connection
            result = self.client.table("users").select("count", count="exact").execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    # User authentication database operations
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        self._ensure_connection()
        try:
            result = self.client.table("users")\
                .select("*")\
                .eq("username", username)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        self._ensure_connection()
        try:
            result = self.client.table("users")\
                .select("*")\
                .eq("email", email)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def create_user(self, username: str, email: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        self._ensure_connection()
        try:
            result = self.client.table("users").insert({
                "username": username,
                "email": email,
                "password_hash": password_hash
            }).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        self._ensure_connection()
        try:
            result = self.client.table("users")\
                .select("id", "username", "email", "created_at", "updated_at")\
                .eq("id", user_id)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    # Trip plan persistence operations
    def save_trip_plan(self, trip_plan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save a complete trip plan with itinerary and cost breakdown"""
        self._ensure_connection()
        try:
            # Insert trip plan
            trip_result = self.client.table("trip_plans").insert({
                "user_id": trip_plan_data["user_id"],
                "destination": trip_plan_data["destination"],
                "start_date": trip_plan_data["start_date"],
                "end_date": trip_plan_data["end_date"],
                "travel_days": trip_plan_data["travel_days"],
                "travel_type": trip_plan_data["travel_type"],
                "budget_preference": trip_plan_data["budget_preference"],
                "max_budget_inr": trip_plan_data["max_budget_inr"],
                "interests": trip_plan_data["interests"],
                "total_cost_inr": trip_plan_data["total_cost_inr"],
                "budget_status": trip_plan_data["budget_status"]
            }).execute()
            
            if not trip_result.data:
                return None
            
            trip_plan_id = trip_result.data[0]["id"]
            
            # Insert itinerary days
            if "itinerary_days" in trip_plan_data:
                for day_data in trip_plan_data["itinerary_days"]:
                    self.client.table("itineraries").insert({
                        "trip_plan_id": trip_plan_id,
                        "day_number": day_data["day_number"],
                        "date": day_data["date"],
                        "activities": day_data["activities"],
                        "weather_info": day_data["weather_info"],
                        "daily_cost_inr": day_data["daily_cost_inr"]
                    }).execute()
            
            # Insert cost breakdown
            if "cost_breakdown" in trip_plan_data:
                cost_data = trip_plan_data["cost_breakdown"]
                self.client.table("cost_breakdowns").insert({
                    "trip_plan_id": trip_plan_id,
                    "flight_cost_inr": cost_data["flight_cost_inr"],
                    "hotel_cost_inr": cost_data["hotel_cost_inr"],
                    "attractions_cost_inr": cost_data["attractions_cost_inr"],
                    "events_cost_inr": cost_data["events_cost_inr"],
                    "local_expenses_inr": cost_data["local_expenses_inr"]
                }).execute()
            
            return trip_result.data[0]
            
        except Exception as e:
            logger.error(f"Error saving trip plan: {e}")
            return None
    
    def get_saved_trips(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all saved trip plans for a user"""
        self._ensure_connection()
        try:
            # Get trip plans
            trip_result = self.client.table("trip_plans")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            if not trip_result.data:
                return []
            
            trips = []
            for trip in trip_result.data:
                # Get itinerary for this trip
                itinerary_result = self.client.table("itineraries")\
                    .select("*")\
                    .eq("trip_plan_id", trip["id"])\
                    .order("day_number")\
                    .execute()
                
                # Get cost breakdown for this trip
                cost_result = self.client.table("cost_breakdowns")\
                    .select("*")\
                    .eq("trip_plan_id", trip["id"])\
                    .execute()
                
                trip["itinerary_days"] = itinerary_result.data
                trip["cost_breakdown"] = cost_result.data[0] if cost_result.data else None
                trips.append(trip)
            
            return trips
            
        except Exception as e:
            logger.error(f"Error getting saved trips: {e}")
            return []
    
    def get_trip_plan_by_id(self, trip_plan_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get a specific trip plan by ID, optionally filtered by user"""
        self._ensure_connection()
        try:
            query = self.client.table("trip_plans").select("*").eq("id", trip_plan_id)
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            trip_result = query.execute()
            
            if not trip_result.data:
                return None
            
            trip = trip_result.data[0]
            
            # Get itinerary for this trip
            itinerary_result = self.client.table("itineraries")\
                .select("*")\
                .eq("trip_plan_id", trip["id"])\
                .order("day_number")\
                .execute()
            
            # Get cost breakdown for this trip
            cost_result = self.client.table("cost_breakdowns")\
                .select("*")\
                .eq("trip_plan_id", trip["id"])\
                .execute()
            
            trip["itinerary_days"] = itinerary_result.data
            trip["cost_breakdown"] = cost_result.data[0] if cost_result.data else None
            
            return trip
            
        except Exception as e:
            logger.error(f"Error getting trip plan by ID: {e}")
            return None
    
    def delete_trip_plan(self, trip_plan_id: str, user_id: str) -> bool:
        """Delete a trip plan (only by the owner)"""
        self._ensure_connection()
        try:
            # Verify ownership and delete
            result = self.client.table("trip_plans")\
                .delete()\
                .eq("id", trip_plan_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting trip plan: {e}")
            return False
    
    def compare_trip_plans(self, trip_plan_ids: List[str], user_id: str) -> List[Dict[str, Any]]:
        """Get multiple trip plans for comparison (only user's own trips)"""
        self._ensure_connection()
        try:
            trips = []
            for trip_id in trip_plan_ids:
                trip = self.get_trip_plan_by_id(trip_id, user_id)
                if trip:
                    trips.append(trip)
            
            return trips
            
        except Exception as e:
            logger.error(f"Error comparing trip plans: {e}")
            return []

# Global database instance
db = Database()