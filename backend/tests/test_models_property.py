"""
Property-based tests for data model validation.

Tests universal properties that should hold across all valid inputs
using Hypothesis for comprehensive input coverage.

Feature: ai-travel-planner, Property 1: Form Input Validation
"""

import pytest
from hypothesis import given, strategies as st, assume
from pydantic import ValidationError

from app.models import (
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

# Invalid string strategy (empty or whitespace-only)
invalid_strings = st.one_of(
    st.just(""),
    st.text().filter(lambda x: not x.strip())
)


class TestTripRequestPropertyValidation:
    """Property-based tests for TripRequest validation.
    
    Feature: ai-travel-planner, Property 1: Form Input Validation
    Validates: Requirements 1.7
    """
    
    @given(
        destination=valid_strings,
        days=st.integers(min_value=1, max_value=30),
        budget=budget_categories,
        travelers=traveler_types
    )
    def test_valid_trip_request_always_succeeds(self, destination, days, budget, travelers):
        """
        Property: For any valid trip planning form submission with all required fields 
        properly filled, the validation should always succeed.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        Validates: Requirements 1.7
        """
        # Valid inputs should always create a successful TripRequest
        trip_request = TripRequest(
            destination=destination,
            days=days,
            budget=budget,
            travelers=travelers
        )
        
        # Verify the object was created successfully
        assert trip_request.destination == destination.strip()
        assert trip_request.days == days
        assert trip_request.budget == budget
        assert trip_request.travelers == travelers
    
    @given(
        destination=invalid_strings,
        days=st.integers(min_value=1, max_value=30),
        budget=budget_categories,
        travelers=traveler_types
    )
    def test_invalid_destination_always_fails(self, destination, days, budget, travelers):
        """
        Property: For any trip planning form submission with invalid destination 
        (empty or whitespace-only), the validation should always fail.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        Validates: Requirements 1.7
        """
        # Invalid destination should always raise ValidationError
        with pytest.raises(ValidationError):
            TripRequest(
                destination=destination,
                days=days,
                budget=budget,
                travelers=travelers
            )
    
    @given(
        destination=valid_strings,
        days=st.one_of(
            st.integers(max_value=0),  # Too small
            st.integers(min_value=31)  # Too large
        ),
        budget=budget_categories,
        travelers=traveler_types
    )
    def test_invalid_days_always_fails(self, destination, days, budget, travelers):
        """
        Property: For any trip planning form submission with invalid days 
        (less than 1 or greater than 30), the validation should always fail.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        Validates: Requirements 1.7
        """
        # Invalid days should always raise ValidationError
        with pytest.raises(ValidationError):
            TripRequest(
                destination=destination,
                days=days,
                budget=budget,
                travelers=travelers
            )


class TestActivityPropertyValidation:
    """Property-based tests for Activity validation."""
    
    @given(
        name=valid_strings,
        description=valid_strings,
        duration=st.integers(min_value=30, max_value=480),
        cost=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        category=activity_categories
    )
    def test_valid_activity_always_succeeds(self, name, description, duration, cost, category):
        """
        Property: For any valid activity data, the validation should always succeed.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        """
        activity = Activity(
            name=name,
            description=description,
            duration=duration,
            cost=cost,
            category=category
        )
        
        assert activity.name == name.strip()
        assert activity.description == description.strip()
        assert activity.duration == duration
        assert activity.cost == cost
        assert activity.category == category
    
    @given(
        name=invalid_strings,
        description=valid_strings,
        duration=st.integers(min_value=30, max_value=480),
        cost=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        category=activity_categories
    )
    def test_invalid_name_always_fails(self, name, description, duration, cost, category):
        """
        Property: For any activity with invalid name (empty or whitespace-only), 
        the validation should always fail.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        """
        with pytest.raises(ValidationError):
            Activity(
                name=name,
                description=description,
                duration=duration,
                cost=cost,
                category=category
            )


class TestTransportOptionPropertyValidation:
    """Property-based tests for TransportOption validation."""
    
    @given(
        transport_type=transport_types,
        provider=valid_strings,
        cost=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        duration=st.integers(min_value=1, max_value=1440),  # 1 minute to 24 hours
        route=valid_strings
    )
    def test_valid_transport_option_always_succeeds(self, transport_type, provider, cost, duration, route):
        """
        Property: For any valid transport option data, the validation should always succeed.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        """
        transport = TransportOption(
            type=transport_type,
            provider=provider,
            cost=cost,
            duration=duration,
            route=route
        )
        
        assert transport.type == transport_type
        assert transport.provider == provider.strip()
        assert transport.cost == cost
        assert transport.duration == duration
        assert transport.route == route.strip()


class TestDayPlanPropertyValidation:
    """Property-based tests for DayPlan validation."""
    
    @given(
        day_number=st.integers(min_value=1, max_value=30),
        activities=st.lists(
            st.builds(
                Activity,
                name=valid_strings,
                description=valid_strings,
                duration=st.integers(min_value=30, max_value=480),
                cost=st.floats(min_value=5.0, max_value=1000.0, allow_nan=False, allow_infinity=False),  # Avoid 0.0 cost
                category=activity_categories
            ),
            min_size=1,
            max_size=10
        ),
        transport=st.lists(
            st.builds(
                TransportOption,
                type=transport_types,
                provider=valid_strings,
                cost=st.floats(min_value=0.0, max_value=500.0, allow_nan=False, allow_infinity=False),
                duration=st.integers(min_value=1, max_value=300),
                route=valid_strings
            ),
            min_size=0,
            max_size=5
        )
    )
    def test_reasonable_cost_validation(self, day_number, activities, transport):
        """
        Property: For any day plan, if the estimated cost is reasonable compared to 
        the sum of activity and transport costs, the validation should succeed.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        """
        # Calculate base cost from activities and transport
        activity_cost = sum(activity.cost for activity in activities)
        transport_cost = sum(t.cost for t in transport)
        base_cost = activity_cost + transport_cost
        
        # Use a reasonable estimated cost that fits within the model's validation range (80%-200%)
        # The model allows estimated_cost between 0.8 * base_cost and 2.0 * base_cost
        estimated_cost = base_cost * 1.2  # 120% of base cost, well within the allowed range
        
        day_plan = DayPlan(
            day_number=day_number,
            activities=activities,
            transport=transport,
            estimated_cost=estimated_cost
        )
        
        assert day_plan.day_number == day_number
        assert len(day_plan.activities) == len(activities)
        assert len(day_plan.transport) == len(transport)
        assert day_plan.estimated_cost == estimated_cost


class TestTripItineraryPropertyValidation:
    """Property-based tests for TripItinerary validation."""
    
    @given(
        trip_id=valid_strings,
        destination=valid_strings,
        total_days=st.integers(min_value=1, max_value=10)  # Smaller range for performance
    )
    def test_sequential_day_numbers_validation(self, trip_id, destination, total_days):
        """
        Property: For any trip itinerary, the day numbers in daily plans must be 
        sequential starting from 1, and the count must match total_days.
        
        Feature: ai-travel-planner, Property 1: Form Input Validation
        """
        # Create activities for each day
        activities = [
            Activity(
                name=f"Activity Day {i+1}",
                description=f"Description for day {i+1}",
                duration=120,
                cost=50.0,
                category=ActivityCategory.SIGHTSEEING
            )
            for i in range(total_days)
        ]
        
        # Create daily plans with sequential day numbers
        daily_plans = [
            DayPlan(
                day_number=i + 1,
                activities=[activities[i]],
                transport=[],
                estimated_cost=60.0
            )
            for i in range(total_days)
        ]
        
        # Calculate reasonable total budget
        total_budget = sum(plan.estimated_cost for plan in daily_plans) * 1.1
        
        itinerary = TripItinerary(
            trip_id=trip_id,
            destination=destination,
            total_days=total_days,
            daily_plans=daily_plans,
            total_budget=total_budget
        )
        
        # Note: TripItinerary doesn't automatically trim strings like other models
        assert itinerary.trip_id == trip_id
        assert itinerary.destination == destination
        assert itinerary.total_days == total_days
        assert len(itinerary.daily_plans) == total_days
        
        # Verify day numbers are sequential
        expected_days = list(range(1, total_days + 1))
        actual_days = [plan.day_number for plan in itinerary.daily_plans]
        assert actual_days == expected_days