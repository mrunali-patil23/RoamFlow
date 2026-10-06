"""
Property-based tests for trip persistence functionality.

These tests verify that trip plan persistence operations maintain data integrity
and correctness across all valid inputs using property-based testing.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import date, timedelta
import uuid
from unittest.mock import Mock, patch

from backend.services.trip_persistence_service import TripPersistenceService
from backend.models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
from backend.models.itinerary_models import TripPlan, Itinerary, DayPlan, Activity, WeatherInfo, ActivityType
from backend.models.cost_models import CostBreakdown, BudgetStatus


# Test data generators
@st.composite
def generate_trip_preferences(draw):
    """Generate valid trip preferences for testing"""
    start_date = draw(st.dates(min_value=date.today() + timedelta(days=1), 
                              max_value=date.today() + timedelta(days=365)))
    travel_days = draw(st.integers(min_value=1, max_value=30))
    end_date = start_date + timedelta(days=travel_days)
    
    # Generate non-empty destination
    destination = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    while not destination.strip():
        destination = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    
    return TripPreferences(
        destination=destination.strip(),
        start_date=start_date,
        end_date=end_date,
        travel_days=travel_days,
        travel_type=draw(st.sampled_from(TravelType)),
        budget_preference=draw(st.sampled_from(BudgetLevel)),
        max_budget_inr=draw(st.floats(min_value=1000.0, max_value=1000000.0)),
        interests=draw(st.lists(st.sampled_from(Interest), min_size=1, max_size=6, unique=True))
    )


@st.composite
def generate_activity(draw):
    """Generate valid activity for testing"""
    # Generate non-empty name
    name = draw(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    while not name.strip():
        name = draw(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    
    # Generate non-empty description
    description = draw(st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    while not description.strip():
        description = draw(st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    
    return Activity(
        name=name.strip(),
        activity_type=draw(st.sampled_from(ActivityType)),
        description=description.strip(),
        duration_hours=draw(st.floats(min_value=0.5, max_value=12.0)),
        cost_inr=draw(st.floats(min_value=0.0, max_value=10000.0)),
        location=draw(st.text(max_size=200)),
        rating=draw(st.one_of(st.none(), st.floats(min_value=1.0, max_value=5.0))),
        start_time=draw(st.one_of(st.none(), st.text(min_size=5, max_size=8))),
        end_time=draw(st.one_of(st.none(), st.text(min_size=5, max_size=8))),
        booking_required=draw(st.booleans())
    )


@st.composite
def generate_weather_info(draw, target_date):
    """Generate valid weather info for testing"""
    # Generate non-empty condition
    condition = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    while not condition.strip():
        condition = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))))
    
    return WeatherInfo(
        date=target_date,
        temperature_high=draw(st.one_of(st.none(), st.floats(min_value=-10.0, max_value=50.0))),
        temperature_low=draw(st.one_of(st.none(), st.floats(min_value=-20.0, max_value=40.0))),
        condition=condition.strip(),
        description=draw(st.text(max_size=200)),
        humidity=draw(st.one_of(st.none(), st.integers(min_value=0, max_value=100))),
        precipitation_chance=draw(st.one_of(st.none(), st.integers(min_value=0, max_value=100)))
    )


@st.composite
def generate_trip_plan(draw):
    """Generate valid trip plan for testing"""
    preferences = draw(generate_trip_preferences())
    user_id = str(uuid.uuid4())
    trip_id = str(uuid.uuid4())
    
    # Generate days
    days = []
    current_date = preferences.start_date
    for day_num in range(1, preferences.travel_days + 1):
        activities = draw(st.lists(generate_activity(), min_size=1, max_size=5))
        weather = draw(generate_weather_info(current_date))
        daily_cost = sum(activity.cost_inr for activity in activities)
        
        day_plan = DayPlan(
            day_number=day_num,
            date=current_date,
            activities=activities,
            weather=weather,
            daily_cost_inr=daily_cost
        )
        days.append(day_plan)
        current_date += timedelta(days=1)
    
    total_cost = sum(day.daily_cost_inr for day in days)
    
    itinerary = Itinerary(
        trip_id=trip_id,
        days=days,
        total_cost_inr=total_cost
    )
    
    cost_breakdown = CostBreakdown(
        flight_cost_inr=draw(st.floats(min_value=0.0, max_value=50000.0)),
        hotel_cost_inr=draw(st.floats(min_value=0.0, max_value=50000.0)),
        attractions_cost_inr=draw(st.floats(min_value=0.0, max_value=20000.0)),
        events_cost_inr=draw(st.floats(min_value=0.0, max_value=20000.0)),
        local_expenses_inr=draw(st.floats(min_value=0.0, max_value=30000.0)),
        total_cost_inr=total_cost,
        daily_breakdown=[]
    )
    
    budget_status = BudgetStatus.calculate_status(total_cost, preferences.max_budget_inr)
    
    return TripPlan(
        id=trip_id,
        user_id=user_id,
        preferences=preferences,
        itinerary=itinerary,
        cost_breakdown=cost_breakdown,
        budget_status=budget_status
    )


class TestTripPersistenceProperties:
    """Property-based tests for trip persistence service"""
    
    @given(generate_trip_plan())
    @settings(max_examples=100)
    def test_property_19_trip_plan_persistence(self, trip_plan):
        """
        Feature: ai-trip-planner, Property 19: Trip Plan Persistence
        For any generated trip plan, all components (preferences, itinerary, costs) 
        should be stored and retrievable from the database
        **Validates: Requirements 7.1**
        """
        # Mock database operations
        mock_db_result = {
            "id": trip_plan.id,
            "user_id": trip_plan.user_id,
            "destination": trip_plan.preferences.destination,
            "start_date": trip_plan.preferences.start_date.isoformat(),
            "end_date": trip_plan.preferences.end_date.isoformat(),
            "travel_days": trip_plan.preferences.travel_days,
            "travel_type": trip_plan.preferences.travel_type.value,
            "budget_preference": trip_plan.preferences.budget_preference.value,
            "max_budget_inr": trip_plan.preferences.max_budget_inr,
            "interests": [interest.value for interest in trip_plan.preferences.interests],
            "total_cost_inr": trip_plan.cost_breakdown.total_cost_inr,
            "budget_status": trip_plan.budget_status.status,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Mock itinerary days
        itinerary_days = []
        for day in trip_plan.itinerary.days:
            activities_json = []
            for activity in day.activities:
                activities_json.append({
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
                })
            
            itinerary_days.append({
                "day_number": day.day_number,
                "date": day.date.isoformat(),
                "activities": activities_json,
                "weather_info": {
                    "date": day.weather.date.isoformat(),
                    "temperature_high": day.weather.temperature_high,
                    "temperature_low": day.weather.temperature_low,
                    "condition": day.weather.condition,
                    "description": day.weather.description,
                    "humidity": day.weather.humidity,
                    "precipitation_chance": day.weather.precipitation_chance
                },
                "daily_cost_inr": day.daily_cost_inr
            })
        
        mock_db_result["itinerary_days"] = itinerary_days
        mock_db_result["cost_breakdown"] = {
            "flight_cost_inr": trip_plan.cost_breakdown.flight_cost_inr,
            "hotel_cost_inr": trip_plan.cost_breakdown.hotel_cost_inr,
            "attractions_cost_inr": trip_plan.cost_breakdown.attractions_cost_inr,
            "events_cost_inr": trip_plan.cost_breakdown.events_cost_inr,
            "local_expenses_inr": trip_plan.cost_breakdown.local_expenses_inr
        }
        
        service = TripPersistenceService()
        
        with patch.object(service.db, 'save_trip_plan') as mock_save, \
             patch.object(service.db, 'get_trip_plan_by_id') as mock_get:
            
            # Mock successful save
            mock_save.return_value = {"id": trip_plan.id}
            mock_get.return_value = mock_db_result
            
            # Test save operation
            saved_id = service.save_trip_plan(trip_plan)
            assert saved_id == trip_plan.id
            
            # Verify save was called with correct data
            mock_save.assert_called_once()
            save_args = mock_save.call_args[0][0]
            
            # Verify all components are preserved
            assert save_args["user_id"] == trip_plan.user_id
            assert save_args["destination"] == trip_plan.preferences.destination
            assert save_args["travel_days"] == trip_plan.preferences.travel_days
            assert save_args["travel_type"] == trip_plan.preferences.travel_type.value
            assert save_args["budget_preference"] == trip_plan.preferences.budget_preference.value
            assert save_args["max_budget_inr"] == trip_plan.preferences.max_budget_inr
            assert len(save_args["interests"]) == len(trip_plan.preferences.interests)
            assert save_args["total_cost_inr"] == trip_plan.cost_breakdown.total_cost_inr
            assert save_args["budget_status"] == trip_plan.budget_status.status
            
            # Verify itinerary data is preserved
            assert len(save_args["itinerary_days"]) == len(trip_plan.itinerary.days)
            for i, day_data in enumerate(save_args["itinerary_days"]):
                original_day = trip_plan.itinerary.days[i]
                assert day_data["day_number"] == original_day.day_number
                assert len(day_data["activities"]) == len(original_day.activities)
                assert day_data["daily_cost_inr"] == original_day.daily_cost_inr
            
            # Verify cost breakdown is preserved
            cost_data = save_args["cost_breakdown"]
            assert cost_data["flight_cost_inr"] == trip_plan.cost_breakdown.flight_cost_inr
            assert cost_data["hotel_cost_inr"] == trip_plan.cost_breakdown.hotel_cost_inr
            assert cost_data["attractions_cost_inr"] == trip_plan.cost_breakdown.attractions_cost_inr
            assert cost_data["events_cost_inr"] == trip_plan.cost_breakdown.events_cost_inr
            assert cost_data["local_expenses_inr"] == trip_plan.cost_breakdown.local_expenses_inr
            
            # Test retrieval operation
            retrieved_trip = service.get_trip_plan_by_id(trip_plan.id, trip_plan.user_id)
            assert retrieved_trip is not None
            
            # Verify retrieved data matches original
            assert retrieved_trip.id == trip_plan.id
            assert retrieved_trip.user_id == trip_plan.user_id
            assert retrieved_trip.preferences.destination == trip_plan.preferences.destination
            assert retrieved_trip.preferences.travel_days == trip_plan.preferences.travel_days
            assert retrieved_trip.preferences.travel_type == trip_plan.preferences.travel_type
            assert retrieved_trip.preferences.budget_preference == trip_plan.preferences.budget_preference
            assert retrieved_trip.preferences.max_budget_inr == trip_plan.preferences.max_budget_inr
            assert len(retrieved_trip.preferences.interests) == len(trip_plan.preferences.interests)
            assert retrieved_trip.cost_breakdown.total_cost_inr == trip_plan.cost_breakdown.total_cost_inr
            assert len(retrieved_trip.itinerary.days) == len(trip_plan.itinerary.days)
    
    @given(st.lists(generate_trip_plan(), min_size=2, max_size=5))
    @settings(max_examples=100)
    def test_property_20_user_data_isolation(self, trip_plans):
        """
        Feature: ai-trip-planner, Property 20: User Data Isolation
        For any user requesting saved plans, only that user's own trip plans should be returned
        **Validates: Requirements 7.2**
        """
        # Ensure we have different users
        for i, trip_plan in enumerate(trip_plans):
            trip_plan.user_id = f"user_{i}"
        
        service = TripPersistenceService()
        
        # Create mock database results for each user
        mock_db_results = {}
        for trip_plan in trip_plans:
            mock_db_result = {
                "id": trip_plan.id,
                "user_id": trip_plan.user_id,
                "destination": trip_plan.preferences.destination,
                "start_date": trip_plan.preferences.start_date.isoformat(),
                "end_date": trip_plan.preferences.end_date.isoformat(),
                "travel_days": trip_plan.preferences.travel_days,
                "travel_type": trip_plan.preferences.travel_type.value,
                "budget_preference": trip_plan.preferences.budget_preference.value,
                "max_budget_inr": trip_plan.preferences.max_budget_inr,
                "interests": [interest.value for interest in trip_plan.preferences.interests],
                "total_cost_inr": trip_plan.cost_breakdown.total_cost_inr,
                "budget_status": trip_plan.budget_status.status,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "itinerary_days": [],
                "cost_breakdown": {
                    "flight_cost_inr": trip_plan.cost_breakdown.flight_cost_inr,
                    "hotel_cost_inr": trip_plan.cost_breakdown.hotel_cost_inr,
                    "attractions_cost_inr": trip_plan.cost_breakdown.attractions_cost_inr,
                    "events_cost_inr": trip_plan.cost_breakdown.events_cost_inr,
                    "local_expenses_inr": trip_plan.cost_breakdown.local_expenses_inr
                }
            }
            
            if trip_plan.user_id not in mock_db_results:
                mock_db_results[trip_plan.user_id] = []
            mock_db_results[trip_plan.user_id].append(mock_db_result)
        
        def mock_get_saved_trips(user_id: str):
            """Mock function that returns only trips for the specified user"""
            return mock_db_results.get(user_id, [])
        
        with patch.object(service.db, 'get_saved_trips', side_effect=mock_get_saved_trips):
            # Test that each user only gets their own trips
            for user_id in mock_db_results.keys():
                user_trips = service.get_saved_trips(user_id)
                
                # Verify all returned trips belong to the requesting user
                for trip in user_trips:
                    assert trip.user_id == user_id
                
                # Verify the count matches expected trips for this user
                expected_count = len(mock_db_results[user_id])
                assert len(user_trips) == expected_count
                
                # Verify no trips from other users are returned
                returned_trip_ids = {trip.id for trip in user_trips}
                expected_trip_ids = {trip["id"] for trip in mock_db_results[user_id]}
                assert returned_trip_ids == expected_trip_ids
                
                # Verify no cross-contamination with other users' data
                for other_user_id, other_trips in mock_db_results.items():
                    if other_user_id != user_id:
                        other_trip_ids = {trip["id"] for trip in other_trips}
                        assert returned_trip_ids.isdisjoint(other_trip_ids), \
                            f"User {user_id} received trips from user {other_user_id}"
    
    @given(st.lists(generate_trip_plan(), min_size=2, max_size=5))
    @settings(max_examples=100)
    def test_property_21_trip_comparison_display(self, trip_plans):
        """
        Feature: ai-trip-planner, Property 21: Trip Comparison Display
        For any set of saved trip plans, the comparison view should display all plans 
        with consistent formatting and structure
        **Validates: Requirements 7.3**
        """
        # Ensure all trips belong to the same user for comparison
        user_id = "test_user_123"
        for trip_plan in trip_plans:
            trip_plan.user_id = user_id
        
        service = TripPersistenceService()
        
        # Create mock database results for comparison
        mock_db_results = []
        trip_plan_ids = []
        
        for trip_plan in trip_plans:
            trip_plan_ids.append(trip_plan.id)
            
            # Create minimal itinerary days for comparison
            itinerary_days = []
            for day in trip_plan.itinerary.days:
                activities_json = []
                for activity in day.activities:
                    activities_json.append({
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
                    })
                
                itinerary_days.append({
                    "day_number": day.day_number,
                    "date": day.date.isoformat(),
                    "activities": activities_json,
                    "weather_info": {
                        "date": day.weather.date.isoformat(),
                        "temperature_high": day.weather.temperature_high,
                        "temperature_low": day.weather.temperature_low,
                        "condition": day.weather.condition,
                        "description": day.weather.description,
                        "humidity": day.weather.humidity,
                        "precipitation_chance": day.weather.precipitation_chance
                    },
                    "daily_cost_inr": day.daily_cost_inr
                })
            
            mock_db_result = {
                "id": trip_plan.id,
                "user_id": trip_plan.user_id,
                "destination": trip_plan.preferences.destination,
                "start_date": trip_plan.preferences.start_date.isoformat(),
                "end_date": trip_plan.preferences.end_date.isoformat(),
                "travel_days": trip_plan.preferences.travel_days,
                "travel_type": trip_plan.preferences.travel_type.value,
                "budget_preference": trip_plan.preferences.budget_preference.value,
                "max_budget_inr": trip_plan.preferences.max_budget_inr,
                "interests": [interest.value for interest in trip_plan.preferences.interests],
                "total_cost_inr": trip_plan.cost_breakdown.total_cost_inr,
                "budget_status": trip_plan.budget_status.status,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "itinerary_days": itinerary_days,
                "cost_breakdown": {
                    "flight_cost_inr": trip_plan.cost_breakdown.flight_cost_inr,
                    "hotel_cost_inr": trip_plan.cost_breakdown.hotel_cost_inr,
                    "attractions_cost_inr": trip_plan.cost_breakdown.attractions_cost_inr,
                    "events_cost_inr": trip_plan.cost_breakdown.events_cost_inr,
                    "local_expenses_inr": trip_plan.cost_breakdown.local_expenses_inr
                }
            }
            mock_db_results.append(mock_db_result)
        
        with patch.object(service.db, 'compare_trip_plans', return_value=mock_db_results):
            # Test trip comparison functionality
            compared_trips = service.compare_trip_plans(trip_plan_ids, user_id)
            
            # Verify all requested trips are returned
            assert len(compared_trips) == len(trip_plans)
            
            # Verify consistent structure across all compared trips
            for i, compared_trip in enumerate(compared_trips):
                original_trip = trip_plans[i]
                
                # Verify all trips have the same structural components
                assert hasattr(compared_trip, 'id')
                assert hasattr(compared_trip, 'user_id')
                assert hasattr(compared_trip, 'preferences')
                assert hasattr(compared_trip, 'itinerary')
                assert hasattr(compared_trip, 'cost_breakdown')
                assert hasattr(compared_trip, 'budget_status')
                assert hasattr(compared_trip, 'created_at')
                assert hasattr(compared_trip, 'updated_at')
                
                # Verify preferences structure consistency
                assert hasattr(compared_trip.preferences, 'destination')
                assert hasattr(compared_trip.preferences, 'start_date')
                assert hasattr(compared_trip.preferences, 'end_date')
                assert hasattr(compared_trip.preferences, 'travel_days')
                assert hasattr(compared_trip.preferences, 'travel_type')
                assert hasattr(compared_trip.preferences, 'budget_preference')
                assert hasattr(compared_trip.preferences, 'max_budget_inr')
                assert hasattr(compared_trip.preferences, 'interests')
                
                # Verify itinerary structure consistency
                assert hasattr(compared_trip.itinerary, 'trip_id')
                assert hasattr(compared_trip.itinerary, 'days')
                assert hasattr(compared_trip.itinerary, 'total_cost_inr')
                assert isinstance(compared_trip.itinerary.days, list)
                
                # Verify cost breakdown structure consistency
                assert hasattr(compared_trip.cost_breakdown, 'flight_cost_inr')
                assert hasattr(compared_trip.cost_breakdown, 'hotel_cost_inr')
                assert hasattr(compared_trip.cost_breakdown, 'attractions_cost_inr')
                assert hasattr(compared_trip.cost_breakdown, 'events_cost_inr')
                assert hasattr(compared_trip.cost_breakdown, 'local_expenses_inr')
                assert hasattr(compared_trip.cost_breakdown, 'total_cost_inr')
                
                # Verify budget status structure consistency
                assert hasattr(compared_trip.budget_status, 'status')
                assert hasattr(compared_trip.budget_status, 'difference_inr')
                assert hasattr(compared_trip.budget_status, 'suggestions')
                
                # Verify data integrity is maintained
                assert compared_trip.id == original_trip.id
                assert compared_trip.user_id == user_id
                assert compared_trip.preferences.destination == original_trip.preferences.destination
                assert compared_trip.preferences.travel_days == original_trip.preferences.travel_days
                assert compared_trip.cost_breakdown.total_cost_inr == original_trip.cost_breakdown.total_cost_inr
                
                # Verify day structure consistency within itinerary
                for day in compared_trip.itinerary.days:
                    assert hasattr(day, 'day_number')
                    assert hasattr(day, 'date')
                    assert hasattr(day, 'activities')
                    assert hasattr(day, 'weather')
                    assert hasattr(day, 'daily_cost_inr')
                    assert isinstance(day.activities, list)
                    
                    # Verify activity structure consistency
                    for activity in day.activities:
                        assert hasattr(activity, 'name')
                        assert hasattr(activity, 'activity_type')
                        assert hasattr(activity, 'description')
                        assert hasattr(activity, 'duration_hours')
                        assert hasattr(activity, 'cost_inr')
                        assert hasattr(activity, 'location')
                        assert hasattr(activity, 'booking_required')
                    
                    # Verify weather structure consistency
                    assert hasattr(day.weather, 'date')
                    assert hasattr(day.weather, 'condition')
                    assert hasattr(day.weather, 'description')
            
            # Verify all trips are from the same user (for valid comparison)
            user_ids = {trip.user_id for trip in compared_trips}
            assert len(user_ids) == 1, "All compared trips should belong to the same user"
            assert user_ids.pop() == user_id
            
            # Verify trips maintain their unique identities
            trip_ids = {trip.id for trip in compared_trips}
            assert len(trip_ids) == len(compared_trips), "All trips should have unique IDs"


if __name__ == "__main__":
    pytest.main([__file__])