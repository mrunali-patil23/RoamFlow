"""
Database service for the AI Travel Planner.

This module provides database operations for trips and user preferences,
supporting both Supabase and MongoDB backends.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from supabase import create_client, Client as SupabaseClient
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from ..models.trip_models import TripItinerary, TripRequest, BudgetCategory, TravelerType


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    async def save_trip(self, trip: TripItinerary) -> str:
        """Save a trip itinerary and return the trip ID."""
        pass
    
    @abstractmethod
    async def get_trip(self, trip_id: str) -> Optional[TripItinerary]:
        """Retrieve a trip by ID."""
        pass
    
    @abstractmethod
    async def get_user_trips(self, user_id: str) -> List[TripItinerary]:
        """Get all trips for a user."""
        pass
    
    @abstractmethod
    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences."""
        pass
    
    @abstractmethod
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        pass
    
    @abstractmethod
    async def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip by ID."""
        pass


class SupabaseService(DatabaseInterface):
    """Supabase database service implementation."""
    
    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        self.client: SupabaseClient = create_client(supabase_url, supabase_key)
    
    async def save_trip(self, trip: TripItinerary) -> str:
        """Save a trip itinerary to Supabase."""
        try:
            # Convert TripItinerary to dict for storage
            trip_data = {
                "id": trip.trip_id,
                "destination": trip.destination,
                "total_days": trip.total_days,
                "itinerary": trip.dict(),  # Store full itinerary as JSONB
                "created_at": trip.created_at.isoformat() if trip.created_at else datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert or update trip
            result = self.client.table("trips").upsert(trip_data).execute()
            
            if result.data:
                return trip.trip_id
            else:
                raise Exception("Failed to save trip to database")
                
        except Exception as e:
            raise Exception(f"Error saving trip to Supabase: {str(e)}")
    
    async def get_trip(self, trip_id: str) -> Optional[TripItinerary]:
        """Retrieve a trip by ID from Supabase."""
        try:
            result = self.client.table("trips").select("*").eq("id", trip_id).execute()
            
            if result.data and len(result.data) > 0:
                trip_data = result.data[0]
                # Reconstruct TripItinerary from stored data
                return TripItinerary(**trip_data["itinerary"])
            
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving trip from Supabase: {str(e)}")
    
    async def get_user_trips(self, user_id: str) -> List[TripItinerary]:
        """Get all trips for a user from Supabase."""
        try:
            result = self.client.table("trips").select("*").eq("user_id", user_id).execute()
            
            trips = []
            if result.data:
                for trip_data in result.data:
                    trips.append(TripItinerary(**trip_data["itinerary"]))
            
            return trips
            
        except Exception as e:
            raise Exception(f"Error retrieving user trips from Supabase: {str(e)}")
    
    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences to Supabase."""
        try:
            pref_data = {
                "user_id": user_id,
                "preferred_budget": preferences.get("preferred_budget"),
                "preferred_traveler_type": preferences.get("preferred_traveler_type"),
                "favorite_destinations": preferences.get("favorite_destinations", []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("user_preferences").upsert(pref_data).execute()
            return bool(result.data)
            
        except Exception as e:
            raise Exception(f"Error saving user preferences to Supabase: {str(e)}")
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences from Supabase."""
        try:
            result = self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving user preferences from Supabase: {str(e)}")
    
    async def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip by ID from Supabase."""
        try:
            result = self.client.table("trips").delete().eq("id", trip_id).execute()
            return bool(result.data)
            
        except Exception as e:
            raise Exception(f"Error deleting trip from Supabase: {str(e)}")


class MongoDBService(DatabaseInterface):
    """MongoDB database service implementation."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            raise ValueError("MONGODB_URL environment variable is required")
        
        self.client = MongoClient(mongodb_url)
        self.db: Database = self.client.travel_planner
        self.trips_collection: Collection = self.db.trips
        self.preferences_collection: Collection = self.db.user_preferences
    
    async def save_trip(self, trip: TripItinerary) -> str:
        """Save a trip itinerary to MongoDB."""
        try:
            # Convert TripItinerary to dict for storage
            trip_data = trip.dict()
            trip_data["_id"] = trip.trip_id
            trip_data["created_at"] = trip.created_at or datetime.utcnow()
            trip_data["updated_at"] = datetime.utcnow()
            
            # Insert or update trip
            result = self.trips_collection.replace_one(
                {"_id": trip.trip_id},
                trip_data,
                upsert=True
            )
            
            if result.acknowledged:
                return trip.trip_id
            else:
                raise Exception("Failed to save trip to database")
                
        except Exception as e:
            raise Exception(f"Error saving trip to MongoDB: {str(e)}")
    
    async def get_trip(self, trip_id: str) -> Optional[TripItinerary]:
        """Retrieve a trip by ID from MongoDB."""
        try:
            trip_data = self.trips_collection.find_one({"_id": trip_id})
            
            if trip_data:
                # Remove MongoDB-specific fields
                trip_data.pop("_id", None)
                trip_data.pop("updated_at", None)
                return TripItinerary(**trip_data)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving trip from MongoDB: {str(e)}")
    
    async def get_user_trips(self, user_id: str) -> List[TripItinerary]:
        """Get all trips for a user from MongoDB."""
        try:
            cursor = self.trips_collection.find({"user_id": user_id})
            
            trips = []
            for trip_data in cursor:
                # Remove MongoDB-specific fields
                trip_data.pop("_id", None)
                trip_data.pop("updated_at", None)
                trips.append(TripItinerary(**trip_data))
            
            return trips
            
        except Exception as e:
            raise Exception(f"Error retrieving user trips from MongoDB: {str(e)}")
    
    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences to MongoDB."""
        try:
            pref_data = {
                "_id": user_id,
                "user_id": user_id,
                "preferred_budget": preferences.get("preferred_budget"),
                "preferred_traveler_type": preferences.get("preferred_traveler_type"),
                "favorite_destinations": preferences.get("favorite_destinations", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.preferences_collection.replace_one(
                {"_id": user_id},
                pref_data,
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            raise Exception(f"Error saving user preferences to MongoDB: {str(e)}")
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences from MongoDB."""
        try:
            pref_data = self.preferences_collection.find_one({"_id": user_id})
            
            if pref_data:
                # Remove MongoDB-specific fields
                pref_data.pop("_id", None)
                return pref_data
            
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving user preferences from MongoDB: {str(e)}")
    
    async def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip by ID from MongoDB."""
        try:
            result = self.trips_collection.delete_one({"_id": trip_id})
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Error deleting trip from MongoDB: {str(e)}")


class DatabaseService:
    """
    Main database service that provides a unified interface.
    Automatically selects between Supabase and MongoDB based on environment configuration.
    """
    
    def __init__(self, testing_mode: bool = False):
        """Initialize database service with appropriate backend."""
        # Check if we're in testing mode
        if testing_mode or os.getenv("TESTING") == "1":
            # In testing mode, don't initialize real database connections
            self._db = None
            self.backend_type = "testing"
            return
            
        # Determine which database to use based on environment variables
        if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
            self._db: DatabaseInterface = SupabaseService()
            self.backend_type = "supabase"
        elif os.getenv("MONGODB_URL"):
            self._db: DatabaseInterface = MongoDBService()
            self.backend_type = "mongodb"
        else:
            raise ValueError(
                "No database configuration found. Please set either "
                "(SUPABASE_URL and SUPABASE_KEY) or MONGODB_URL environment variables."
            )
    
    async def save_trip(self, trip: TripItinerary) -> str:
        """Save a trip itinerary."""
        if self._db is None:
            raise RuntimeError("Database service not initialized for production use")
        return await self._db.save_trip(trip)
    
    async def get_trip(self, trip_id: str) -> Optional[TripItinerary]:
        """Retrieve a trip by ID."""
        if self._db is None:
            raise RuntimeError("Database service not initialized for production use")
        return await self._db.get_trip(trip_id)
    
    async def get_user_trips(self, user_id: str) -> List[TripItinerary]:
        """Get all trips for a user."""
        if self._db is None:
            raise RuntimeError("Database service not initialized for production use")
        return await self._db.get_user_trips(user_id)
    
    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences."""
        if self._db is None:
            raise RuntimeError("Database service not initialized for production use")
        return await self._db.save_user_preferences(user_id, preferences)
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        if self._db is None:
            raise RuntimeError("Database service not initialized for production use")
        return await self._db.get_user_preferences(user_id)
    
    async def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip by ID."""
        if self._db is None:
            raise RuntimeError("Database service not initialized for production use")
        return await self._db.delete_trip(trip_id)
    
    def get_backend_type(self) -> str:
        """Get the current database backend type."""
        return self.backend_type


# Singleton instance for dependency injection
_database_service = None

def get_database_service() -> DatabaseService:
    """Get or create the database service singleton."""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService(testing_mode=os.getenv("TESTING") == "1")
    return _database_service

# For backward compatibility
database_service = None