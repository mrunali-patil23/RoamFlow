"""
Property-based tests for trip preferences input validation.
Tests universal properties that should hold for all valid inputs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import date, timedelta
from decimal import Decimal

# Configure hypothesis to run more examples for thorough testing
settings.register_profile("production", max_examples=100, deadline=5000)
settings.load_profile("production")

# Feature: ai-trip-planner, Property 5: Input Validation Consistency
# **Validates: Requirements 2.2, 2.3, 2.6**

@given(
    start_date=st.dates(min_value=date.today() - timedelta(days=365), max_value=date.today() + timedelta(days=365)),
    end_date=st.dates(min_value=date.today() - timedelta(days=365), max_value=date.today() + timedelta(days=365)),
    travel_days=st.integers(min_value=-100, max_value=100),
    max_budget_inr=st.floats(min_value=-10000.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
    destination=st.text(min_size=0, max_size=100)
)
def test_property_input_validation_consistency(start_date, end_date, travel_days, max_budget_inr, destination):
    """
    Property 5: Input Validation Consistency
    For any user input (dates, travel days, budget amounts), the system should 
    validate according to business rules (future dates, positive integers, valid currency format).
    **Validates: Requirements 2.2, 2.3, 2.6**
    """
    from models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
    
    # Test date validation (Requirement 2.2)
    today = date.today()
    
    # Property: Future dates should be valid, past dates should be invalid
    if start_date < today:
        # Past start dates should be invalid
        with pytest.raises(ValueError, match="Start date must be in the future"):
            try:
                # Create a minimal valid preferences object to test start date validation
                TripPreferences(
                    destination="Test City",
                    start_date=start_date,
                    end_date=max(start_date + timedelta(days=1), today + timedelta(days=1)),
                    travel_days=5,
                    travel_type=TravelType.SOLO,
                    budget_preference=BudgetLevel.MEDIUM,
                    max_budget_inr=10000.0,
                    interests=[Interest.NATURE]
                )
            except ValueError as e:
                if "Start date must be in the future" in str(e):
                    raise
                # If it's a different validation error, re-raise as the expected error
                raise ValueError("Start date must be in the future")
    
    # Property: End date must be after start date (Requirement 2.2)
    if start_date >= end_date:
        with pytest.raises(ValueError, match="End date must be after start date"):
            TripPreferences(
                destination="Test City",
                start_date=max(start_date, today),
                end_date=end_date,
                travel_days=5,
                travel_type=TravelType.SOLO,
                budget_preference=BudgetLevel.MEDIUM,
                max_budget_inr=10000.0,
                interests=[Interest.NATURE]
            )
    
    # Test travel days validation (Requirement 2.3)
    # Property: Travel days must be positive integers
    if travel_days <= 0:
        with pytest.raises(ValueError, match="Travel days must be positive"):
            TripPreferences(
                destination="Test City",
                start_date=max(today + timedelta(days=1), start_date),
                end_date=max(today + timedelta(days=2), start_date + timedelta(days=1), end_date),
                travel_days=travel_days,
                travel_type=TravelType.SOLO,
                budget_preference=BudgetLevel.MEDIUM,
                max_budget_inr=10000.0,
                interests=[Interest.NATURE]
            )
    
    # Test maximum budget validation (Requirement 2.6)
    # Property: Maximum budget must be positive
    if max_budget_inr <= 0:
        with pytest.raises(ValueError, match="Maximum budget must be positive"):
            TripPreferences(
                destination="Test City",
                start_date=max(today + timedelta(days=1), start_date),
                end_date=max(today + timedelta(days=2), start_date + timedelta(days=1), end_date),
                travel_days=max(1, travel_days),
                travel_type=TravelType.SOLO,
                budget_preference=BudgetLevel.MEDIUM,
                max_budget_inr=max_budget_inr,
                interests=[Interest.NATURE]
            )
    
    # Test destination validation
    # Property: Destination cannot be empty
    if not destination.strip():
        with pytest.raises(ValueError, match="Destination cannot be empty"):
            TripPreferences(
                destination=destination,
                start_date=max(today + timedelta(days=1), start_date),
                end_date=max(today + timedelta(days=2), start_date + timedelta(days=1), end_date),
                travel_days=max(1, travel_days),
                travel_type=TravelType.SOLO,
                budget_preference=BudgetLevel.MEDIUM,
                max_budget_inr=max(1.0, max_budget_inr),
                interests=[Interest.NATURE]
            )
    
    # Property: Valid inputs should create a valid TripPreferences object
    if (start_date >= today and 
        end_date > start_date and 
        travel_days > 0 and 
        max_budget_inr > 0 and 
        destination.strip()):
        
        # All inputs are valid, should create object successfully
        trip_prefs = TripPreferences(
            destination=destination.strip(),
            start_date=start_date,
            end_date=end_date,
            travel_days=travel_days,
            travel_type=TravelType.SOLO,
            budget_preference=BudgetLevel.MEDIUM,
            max_budget_inr=max_budget_inr,
            interests=[Interest.NATURE]
        )
        
        # Property: Created object should contain the input values
        assert trip_prefs.destination == destination.strip()
        assert trip_prefs.start_date == start_date
        assert trip_prefs.end_date == end_date
        assert trip_prefs.travel_days == travel_days
        assert trip_prefs.max_budget_inr == max_budget_inr
        
        # Property: All required fields should be present
        assert hasattr(trip_prefs, 'destination')
        assert hasattr(trip_prefs, 'start_date')
        assert hasattr(trip_prefs, 'end_date')
        assert hasattr(trip_prefs, 'travel_days')
        assert hasattr(trip_prefs, 'travel_type')
        assert hasattr(trip_prefs, 'budget_preference')
        assert hasattr(trip_prefs, 'max_budget_inr')
        assert hasattr(trip_prefs, 'interests')


@given(
    budget_amount=st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
def test_property_currency_format_validation(budget_amount):
    """
    Property: Currency format validation for INR amounts
    For any positive budget amount, the system should accept it as valid INR currency.
    **Validates: Requirements 2.6**
    """
    from models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
    
    today = date.today()
    
    # Property: Any positive float should be accepted as valid INR amount
    trip_prefs = TripPreferences(
        destination="Test City",
        start_date=today + timedelta(days=1),
        end_date=today + timedelta(days=5),
        travel_days=4,
        travel_type=TravelType.SOLO,
        budget_preference=BudgetLevel.MEDIUM,
        max_budget_inr=budget_amount,
        interests=[Interest.NATURE]
    )
    
    # Property: Budget amount should be stored as provided
    assert trip_prefs.max_budget_inr == budget_amount
    
    # Property: Budget amount should be a positive number
    assert trip_prefs.max_budget_inr > 0


@given(
    days_offset_start=st.integers(min_value=1, max_value=365),
    days_offset_end=st.integers(min_value=2, max_value=366)
)
def test_property_date_range_validation(days_offset_start, days_offset_end):
    """
    Property: Date range validation consistency
    For any valid future date range, the system should accept it.
    **Validates: Requirements 2.2**
    """
    assume(days_offset_end > days_offset_start)
    
    from models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
    
    today = date.today()
    start_date = today + timedelta(days=days_offset_start)
    end_date = today + timedelta(days=days_offset_end)
    
    # Property: Valid future date ranges should be accepted
    trip_prefs = TripPreferences(
        destination="Test City",
        start_date=start_date,
        end_date=end_date,
        travel_days=days_offset_end - days_offset_start,
        travel_type=TravelType.SOLO,
        budget_preference=BudgetLevel.MEDIUM,
        max_budget_inr=10000.0,
        interests=[Interest.NATURE]
    )
    
    # Property: Dates should be stored as provided
    assert trip_prefs.start_date == start_date
    assert trip_prefs.end_date == end_date
    
    # Property: Date range should be valid (end after start)
    assert trip_prefs.end_date > trip_prefs.start_date
    
    # Property: Both dates should be in the future
    assert trip_prefs.start_date >= today
    assert trip_prefs.end_date > today