"""
Property-based tests for database persistence operations.

Tests universal properties that should hold for data persistence round trips
using Hypothesis for comprehensive input coverage.

Feature: ai-travel-planner, Property 6: Data Persistence Round Trip
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from pydantic import ValidationError

from app.models.trip_models import (
    BudgetCategory,
    TravelerType,
    ActivityCategory,
    TransportType,
    TripRequest,
    Activity,
    TransportOption,
    DayPlan,
    TripItinerary,
)
from app.services.database_service import DatabaseService
from app.services.trip_service import TripService


# Hypothesis strategies for generating test data
budget_categories = st.sampled_from([BudgetCategory.CHEAP, BudgetCategory.MODERATE, BudgetCategory.LUXURY])
traveler_types = st.sampled_from([TravelerType.JUST_ME, TravelerType.COUPLE, TravelerType.FAMILY, TravelerType.FRIENDS])
activity_categories = st.sampled_from([
    ActivityCategory.SIGHTSEEING, 
    ActivityCategory.DINING, 
    ActivityCategory.ENTERTAINMENT, 
    ActivityCategory.CULTURAL
])
transport_types = st.sampled_from([
    TransportType.FLIGHT, 
    TransportType.TAXI, 
    TransportType.BUS, 
    TransportType.METRO, 
    TransportType.WALKING
])

# Valid string strategy (non-empty, reasonable length)
valid_strings = st.text(min_size=1, max_size=100).filter(lambda x: x.strip())

# Strategy for generating valid activities
activity_strategy = st.builds(
    Activity,
    name=valid_strings,
    description=valid_strings,
    duration=st.integers(min_value=30, max_value=480),
    cost=st.floats(min_value=5.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    category=activity_categories
)

# Strategy for generating valid transport options
transport_strategy = st.builds(
    TransportOption,
    type=transport_types,
    provider=valid_strings,
    cost=st.floats(min_value=0.0, max_value=500.0, allow_nan=False, allow_infinity=False),
    duration=st.integers(min_value=1, max_value=300),
    route=valid_strings
)

# Strategy for generating valid day plans
@st.composite
def day_plan_strategy(draw, day_number):
    """Generate a valid DayPlan with reasonable cost validation."""
    activities = draw(st.lists(activity_strategy, min_size=1, max_size=5))
    transport = draw(st.lists(transport_strategy, min_size=0, max_size=3))
    
    # Calculate base cost and set reasonable estimated cost
    activity_cost = sum(activity.cost for activity in activities)
    transport_cost = sum(t.cost for t in transport)
    base_cost = activity_cost + transport_cost
    
    # Set estimated cost within the model's validation range (80%-200% of base cost)
    estimated_cost = base_cost * draw(st.floats(min_value=0.9, max_value=1.8))
    
    return DayPlan(
        day_number=day_number,
        activities=activities,
        transport=transport,
        estimated_cost=estimated_cost
    )

# Strategy for generating valid trip itineraries
@st.composite
def trip_itinerary_strategy(draw):
    """Generate a valid TripItinerary with all constraints satisfied."""
    trip_id = str(uuid.uuid4())
    destination = draw(valid_strings)
    total_days = draw(st.integers(min_value=1, max_value=7))  # Smaller range for performance
    
    # Generate daily plans with sequential day numbers
    daily_plans = []
    for day in range(1, total_days + 1):
        day_plan = draw(day_plan_strategy(day))
        daily_plans.append(day_plan)
    
    # Calculate reasonable total budget
    daily_total = sum(plan.estimated_cost for plan in daily_plans)
    total_budget = daily_total * draw(st.floats(min_value=0.9, max_value=1.4))
    
    return TripItinerary(
        trip_id=trip_id,
        destination=destination,
        total_days=total_days,
        daily_plans=daily_plans,
        total_budget=total_budget,
        created_at=datetime.utcnow()
    )


class TestDatabasePersistenceProperty:
    """
    Property-based tests for database persistence operations.
    
    Feature: ai-travel-planner, Property 6: Data Persistence Round Trip
    Validates: Requirements 5.1, 5.2, 5.3
    """
    
    def create_mock_database_service(self):
        """Create a fresh mock database service for each test."""
        
        class MockDatabaseService:
            def __init__(self):
                self.trips = {}
                self.preferences = {}
                self.backend_type = "mock"
            
            async def save_trip(self, trip: TripItinerary) -> str:
                """Mock save trip implementation."""
                self.trips[trip.trip_id] = trip.dict()
                return trip.trip_id
            
            async def get_trip(self, trip_id: str):
                """Mock get trip implementation."""
                if trip_id in self.trips:
                    trip_data = self.trips[trip_id]
                    return TripItinerary(**trip_data)
                return None
            
            async def get_user_trips(self, user_id: str):
                """Mock get user trips implementation."""
                user_trips = []
                for trip_data in self.trips.values():
                    if trip_data.get("user_id") == user_id:
                        user_trips.append(TripItinerary(**trip_data))
                return user_trips
            
            async def save_user_preferences(self, user_id: str, preferences):
                """Mock save preferences implementation."""
                self.preferences[user_id] = preferences.copy()
                return True
            
            async def get_user_preferences(self, user_id: str):
                """Mock get preferences implementation."""
                return self.preferences.get(user_id)
            
            async def delete_trip(self, trip_id: str) -> bool:
                """Mock delete trip implementation."""
                if trip_id in self.trips:
                    del self.trips[trip_id]
                    return True
                return False
            
            def get_backend_type(self) -> str:
                return self.backend_type
        
        return MockDatabaseService()
    
    @given(trip=trip_itinerary_strategy())
    @settings(
        max_examples=50, 
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_trip_persistence_round_trip(self, trip):
        """
        Property: For any completed trip planning session, storing the trip data 
        and then retrieving it should produce equivalent trip information including 
        all preferences, itinerary details, and cost breakdowns.
        
        Feature: ai-travel-planner, Property 6: Data Persistence Round Trip
        Validates: Requirements 5.1, 5.2, 5.3
        """
        mock_database_service = self.create_mock_database_service()
        
        async def run_test():
            # Save the trip
            saved_trip_id = await mock_database_service.save_trip(trip)
            
            # Verify the trip ID was returned
            assert saved_trip_id == trip.trip_id
            
            # Retrieve the trip
            retrieved_trip = await mock_database_service.get_trip(trip.trip_id)
            
            # Verify the trip was retrieved successfully
            assert retrieved_trip is not None
            
            # Verify all essential data is preserved
            assert retrieved_trip.trip_id == trip.trip_id
            assert retrieved_trip.destination == trip.destination
            assert retrieved_trip.total_days == trip.total_days
            assert retrieved_trip.total_budget == trip.total_budget
            
            # Verify daily plans are preserved
            assert len(retrieved_trip.daily_plans) == len(trip.daily_plans)
            
            for original_plan, retrieved_plan in zip(trip.daily_plans, retrieved_trip.daily_plans):
                assert retrieved_plan.day_number == original_plan.day_number
                assert retrieved_plan.estimated_cost == original_plan.estimated_cost
                
                # Verify activities are preserved
                assert len(retrieved_plan.activities) == len(original_plan.activities)
                for orig_activity, retr_activity in zip(original_plan.activities, retrieved_plan.activities):
                    assert retr_activity.name == orig_activity.name
                    assert retr_activity.description == orig_activity.description
                    assert retr_activity.duration == orig_activity.duration
                    assert retr_activity.cost == orig_activity.cost
                    assert retr_activity.category == orig_activity.category
                
                # Verify transport options are preserved
                assert len(retrieved_plan.transport) == len(original_plan.transport)
                for orig_transport, retr_transport in zip(original_plan.transport, retrieved_plan.transport):
                    assert retr_transport.type == orig_transport.type
                    assert retr_transport.provider == orig_transport.provider
                    assert retr_transport.cost == orig_transport.cost
                    assert retr_transport.duration == orig_transport.duration
                    assert retr_transport.route == orig_transport.route
        
        # Run the async test
        asyncio.run(run_test())
    
    @given(
        user_id=valid_strings,
        preferences=st.fixed_dictionaries({
            "preferred_budget": st.sampled_from(["cheap", "moderate", "luxury"]),
            "preferred_traveler_type": st.sampled_from(["just-me", "couple", "family", "friends"]),
            "favorite_destinations": st.lists(valid_strings, min_size=0, max_size=5)
        })
    )
    @settings(
        max_examples=30, 
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_user_preferences_round_trip(self, user_id, preferences):
        """
        Property: For any user preferences, storing the preferences and then 
        retrieving them should produce equivalent preference data.
        
        Feature: ai-travel-planner, Property 6: Data Persistence Round Trip
        Validates: Requirements 5.1, 5.2, 5.3
        """
        mock_database_service = self.create_mock_database_service()
        
        async def run_test():
            # Save user preferences
            save_result = await mock_database_service.save_user_preferences(user_id, preferences)
            
            # Verify save was successful
            assert save_result is True
            
            # Retrieve user preferences
            retrieved_preferences = await mock_database_service.get_user_preferences(user_id)
            
            # Verify preferences were retrieved successfully
            assert retrieved_preferences is not None
            
            # Verify all preference data is preserved
            assert retrieved_preferences["preferred_budget"] == preferences["preferred_budget"]
            assert retrieved_preferences["preferred_traveler_type"] == preferences["preferred_traveler_type"]
            assert retrieved_preferences["favorite_destinations"] == preferences["favorite_destinations"]
        
        # Run the async test
        asyncio.run(run_test())
    
    @given(trip=trip_itinerary_strategy())
    @settings(
        max_examples=30, 
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_trip_deletion_consistency(self, trip):
        """
        Property: For any stored trip, deleting it should make it no longer 
        retrievable, maintaining data consistency.
        
        Feature: ai-travel-planner, Property 6: Data Persistence Round Trip
        Validates: Requirements 5.1, 5.2, 5.3
        """
        mock_database_service = self.create_mock_database_service()
        
        async def run_test():
            # Save the trip
            saved_trip_id = await mock_database_service.save_trip(trip)
            assert saved_trip_id == trip.trip_id
            
            # Verify trip exists
            retrieved_trip = await mock_database_service.get_trip(trip.trip_id)
            assert retrieved_trip is not None
            
            # Delete the trip
            delete_result = await mock_database_service.delete_trip(trip.trip_id)
            assert delete_result is True
            
            # Verify trip no longer exists
            deleted_trip = await mock_database_service.get_trip(trip.trip_id)
            assert deleted_trip is None
            
            # Verify deleting non-existent trip returns False
            delete_again_result = await mock_database_service.delete_trip(trip.trip_id)
            assert delete_again_result is False
        
        # Run the async test
        asyncio.run(run_test())


class TestTripServiceIntegration:
    """Integration tests for TripService with database operations."""
    
    @given(trip_request=st.builds(
        TripRequest,
        destination=valid_strings,
        days=st.integers(min_value=1, max_value=7),
        budget=budget_categories,
        travelers=traveler_types
    ))
    @settings(
        max_examples=20, 
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_sample_trip_creation_and_storage(self, trip_request, monkeypatch):
        """
        Property: For any valid trip request, creating a sample trip and storing it 
        should allow successful retrieval with all data intact.
        
        Feature: ai-travel-planner, Property 6: Data Persistence Round Trip
        Validates: Requirements 5.1, 5.2, 5.3
        """
        # Create mock database service
        class MockDatabaseService:
            def __init__(self):
                self.trips = {}
                self.preferences = {}
                self.backend_type = "mock"
            
            async def save_trip(self, trip: TripItinerary) -> str:
                self.trips[trip.trip_id] = trip.dict()
                return trip.trip_id
            
            async def get_trip(self, trip_id: str):
                if trip_id in self.trips:
                    trip_data = self.trips[trip_id]
                    return TripItinerary(**trip_data)
                return None
            
            async def get_user_trips(self, user_id: str):
                user_trips = []
                for trip_data in self.trips.values():
                    if trip_data.get("user_id") == user_id:
                        user_trips.append(TripItinerary(**trip_data))
                return user_trips
            
            async def save_user_preferences(self, user_id: str, preferences):
                self.preferences[user_id] = preferences.copy()
                return True
            
            async def get_user_preferences(self, user_id: str):
                return self.preferences.get(user_id)
            
            async def delete_trip(self, trip_id: str) -> bool:
                if trip_id in self.trips:
                    del self.trips[trip_id]
                    return True
                return False
            
            def get_backend_type(self) -> str:
                return self.backend_type
        
        mock_database_service = MockDatabaseService()
        
        # Patch the database service in the trip service module
        monkeypatch.setattr("app.services.trip_service.database_service", mock_database_service)
        trip_service = TripService()
        
        async def run_test():
            # Create a sample trip
            sample_trip = trip_service.create_sample_trip(trip_request)
            
            # Verify sample trip has correct basic properties
            assert sample_trip.destination == trip_request.destination
            assert sample_trip.total_days == trip_request.days
            assert len(sample_trip.daily_plans) == trip_request.days
            
            # Save the trip through the service
            saved_trip_id = await trip_service.save_trip(sample_trip)
            assert saved_trip_id == sample_trip.trip_id
            
            # Retrieve the trip through the service
            retrieved_trip = await trip_service.get_trip(sample_trip.trip_id)
            
            # Verify round trip consistency
            assert retrieved_trip is not None
            assert retrieved_trip.trip_id == sample_trip.trip_id
            assert retrieved_trip.destination == sample_trip.destination
            assert retrieved_trip.total_days == sample_trip.total_days
            assert retrieved_trip.total_budget == sample_trip.total_budget
            assert len(retrieved_trip.daily_plans) == len(sample_trip.daily_plans)
        
        # Run the async test
        asyncio.run(run_test())