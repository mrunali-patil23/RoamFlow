"""
Unit tests for Pydantic data models.

Tests validation logic, edge cases, and serialization for all data models.
"""

import pytest
from datetime import datetime
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
    APIResponse,
    ErrorResponse,
    FlightSearchParams,
    FlightOption,
    FlightOptions,
    TransportRequest,
    TransportOptions,
)


class TestTripRequest:
    """Test TripRequest model validation."""
    
    def test_valid_trip_request(self):
        """Test creating a valid trip request."""
        request = TripRequest(
            destination="Paris, France",
            days=5,
            budget=BudgetCategory.MODERATE,
            travelers=TravelerType.COUPLE
        )
        assert request.destination == "Paris, France"
        assert request.days == 5
        assert request.budget == BudgetCategory.MODERATE
        assert request.travelers == TravelerType.COUPLE
    
    def test_destination_validation(self):
        """Test destination field validation."""
        # Empty destination should fail
        with pytest.raises(ValidationError) as exc_info:
            TripRequest(
                destination="",
                days=5,
                budget=BudgetCategory.MODERATE,
                travelers=TravelerType.COUPLE
            )
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Whitespace-only destination should fail
        with pytest.raises(ValidationError) as exc_info:
            TripRequest(
                destination="   ",
                days=5,
                budget=BudgetCategory.MODERATE,
                travelers=TravelerType.COUPLE
            )
        assert "Destination cannot be empty" in str(exc_info.value)
        
        # Destination with leading/trailing whitespace should be trimmed
        request = TripRequest(
            destination="  Paris, France  ",
            days=5,
            budget=BudgetCategory.MODERATE,
            travelers=TravelerType.COUPLE
        )
        assert request.destination == "Paris, France"
    
    def test_days_validation(self):
        """Test days field validation."""
        # Days must be at least 1
        with pytest.raises(ValidationError):
            TripRequest(
                destination="Paris, France",
                days=0,
                budget=BudgetCategory.MODERATE,
                travelers=TravelerType.COUPLE
            )
        
        # Days must be at most 30
        with pytest.raises(ValidationError):
            TripRequest(
                destination="Paris, France",
                days=31,
                budget=BudgetCategory.MODERATE,
                travelers=TravelerType.COUPLE
            )
    
    def test_enum_validation(self):
        """Test enum field validation."""
        # Invalid budget should fail
        with pytest.raises(ValidationError):
            TripRequest(
                destination="Paris, France",
                days=5,
                budget="invalid",
                travelers=TravelerType.COUPLE
            )
        
        # Invalid traveler type should fail
        with pytest.raises(ValidationError):
            TripRequest(
                destination="Paris, France",
                days=5,
                budget=BudgetCategory.MODERATE,
                travelers="invalid"
            )


class TestActivity:
    """Test Activity model validation."""
    
    def test_valid_activity(self):
        """Test creating a valid activity."""
        activity = Activity(
            name="Visit Eiffel Tower",
            description="Iconic iron lattice tower and symbol of Paris",
            duration=120,
            cost=25.0,
            category=ActivityCategory.SIGHTSEEING
        )
        assert activity.name == "Visit Eiffel Tower"
        assert activity.duration == 120
        assert activity.cost == 25.0
        assert activity.category == ActivityCategory.SIGHTSEEING
    
    def test_string_field_validation(self):
        """Test string field validation for name and description."""
        # Empty name should fail
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                name="",
                description="Test description",
                duration=120,
                cost=25.0,
                category=ActivityCategory.SIGHTSEEING
            )
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Whitespace-only description should fail
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                name="Test Activity",
                description="   ",
                duration=120,
                cost=25.0,
                category=ActivityCategory.SIGHTSEEING
            )
        assert "Field cannot be empty" in str(exc_info.value)
        
        # Fields with leading/trailing whitespace should be trimmed
        activity = Activity(
            name="  Visit Eiffel Tower  ",
            description="  Great tower  ",
            duration=120,
            cost=25.0,
            category=ActivityCategory.SIGHTSEEING
        )
        assert activity.name == "Visit Eiffel Tower"
        assert activity.description == "Great tower"
    
    def test_duration_validation(self):
        """Test duration field validation."""
        # Duration must be at least 30 minutes
        with pytest.raises(ValidationError):
            Activity(
                name="Quick Activity",
                description="Very quick activity",
                duration=15,
                cost=25.0,
                category=ActivityCategory.SIGHTSEEING
            )
        
        # Duration must be at most 480 minutes (8 hours)
        with pytest.raises(ValidationError):
            Activity(
                name="Long Activity",
                description="Very long activity",
                duration=500,
                cost=25.0,
                category=ActivityCategory.SIGHTSEEING
            )
    
    def test_cost_validation(self):
        """Test cost field validation."""
        # Cost must be non-negative
        with pytest.raises(ValidationError):
            Activity(
                name="Free Activity",
                description="Actually costs money somehow",
                duration=120,
                cost=-10.0,
                category=ActivityCategory.SIGHTSEEING
            )
        
        # Zero cost should be allowed
        activity = Activity(
            name="Free Activity",
            description="Actually free",
            duration=120,
            cost=0.0,
            category=ActivityCategory.SIGHTSEEING
        )
        assert activity.cost == 0.0


class TestTransportOption:
    """Test TransportOption model validation."""
    
    def test_valid_transport_option(self):
        """Test creating a valid transport option."""
        transport = TransportOption(
            type=TransportType.METRO,
            provider="RATP",
            cost=1.90,
            duration=25,
            route="Line 6 from Trocadéro to Eiffel Tower"
        )
        assert transport.type == TransportType.METRO
        assert transport.provider == "RATP"
        assert transport.cost == 1.90
        assert transport.duration == 25
        assert transport.route == "Line 6 from Trocadéro to Eiffel Tower"
    
    def test_string_field_validation(self):
        """Test string field validation for provider and route."""
        # Empty provider should fail
        with pytest.raises(ValidationError) as exc_info:
            TransportOption(
                type=TransportType.METRO,
                provider="",
                cost=1.90,
                duration=25,
                route="Test route"
            )
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Whitespace-only route should fail
        with pytest.raises(ValidationError) as exc_info:
            TransportOption(
                type=TransportType.METRO,
                provider="RATP",
                cost=1.90,
                duration=25,
                route="   "
            )
        assert "Field cannot be empty" in str(exc_info.value)


class TestDayPlan:
    """Test DayPlan model validation."""
    
    def test_valid_day_plan(self):
        """Test creating a valid day plan."""
        activity = Activity(
            name="Visit Eiffel Tower",
            description="Iconic tower",
            duration=120,
            cost=25.0,
            category=ActivityCategory.SIGHTSEEING
        )
        transport = TransportOption(
            type=TransportType.METRO,
            provider="RATP",
            cost=1.90,
            duration=25,
            route="Line 6"
        )
        
        day_plan = DayPlan(
            day_number=1,
            activities=[activity],
            transport=[transport],
            estimated_cost=30.0
        )
        
        assert day_plan.day_number == 1
        assert len(day_plan.activities) == 1
        assert len(day_plan.transport) == 1
        assert day_plan.estimated_cost == 30.0
    
    def test_day_number_validation(self):
        """Test day number validation."""
        activity = Activity(
            name="Test Activity",
            description="Test description",
            duration=120,
            cost=25.0,
            category=ActivityCategory.SIGHTSEEING
        )
        
        # Day number must be at least 1
        with pytest.raises(ValidationError):
            DayPlan(
                day_number=0,
                activities=[activity],
                transport=[],
                estimated_cost=25.0
            )
    
    def test_activities_validation(self):
        """Test activities list validation."""
        # Must have at least one activity
        with pytest.raises(ValidationError):
            DayPlan(
                day_number=1,
                activities=[],
                transport=[],
                estimated_cost=0.0
            )
    
    def test_cost_validation(self):
        """Test estimated cost validation logic."""
        activity = Activity(
            name="Expensive Activity",
            description="Very expensive",
            duration=120,
            cost=100.0,
            category=ActivityCategory.SIGHTSEEING
        )
        transport = TransportOption(
            type=TransportType.TAXI,
            provider="Uber",
            cost=20.0,
            duration=30,
            route="Hotel to attraction"
        )
        
        # Cost too low compared to activities/transport should fail
        with pytest.raises(ValidationError) as exc_info:
            DayPlan(
                day_number=1,
                activities=[activity],
                transport=[transport],
                estimated_cost=50.0  # Much lower than activity (100) + transport (20) = 120
            )
        assert "unreasonable" in str(exc_info.value)
        
        # Cost too high compared to activities/transport should fail
        with pytest.raises(ValidationError) as exc_info:
            DayPlan(
                day_number=1,
                activities=[activity],
                transport=[transport],
                estimated_cost=300.0  # Much higher than activity (100) + transport (20) = 120
            )
        assert "unreasonable" in str(exc_info.value)
        
        # Reasonable cost should pass
        day_plan = DayPlan(
            day_number=1,
            activities=[activity],
            transport=[transport],
            estimated_cost=140.0  # Reasonable compared to 120 base cost
        )
        assert day_plan.estimated_cost == 140.0


class TestTripItinerary:
    """Test TripItinerary model validation."""
    
    def test_valid_trip_itinerary(self):
        """Test creating a valid trip itinerary."""
        activity = Activity(
            name="Test Activity",
            description="Test description",
            duration=120,
            cost=25.0,
            category=ActivityCategory.SIGHTSEEING
        )
        
        day_plan = DayPlan(
            day_number=1,
            activities=[activity],
            transport=[],
            estimated_cost=30.0
        )
        
        itinerary = TripItinerary(
            trip_id="trip_123",
            destination="Paris, France",
            total_days=1,
            daily_plans=[day_plan],
            total_budget=35.0
        )
        
        assert itinerary.trip_id == "trip_123"
        assert itinerary.destination == "Paris, France"
        assert itinerary.total_days == 1
        assert len(itinerary.daily_plans) == 1
        assert itinerary.total_budget == 35.0
        assert itinerary.created_at is not None
    
    def test_daily_plans_count_validation(self):
        """Test that daily plans count matches total days."""
        activity = Activity(
            name="Test Activity",
            description="Test description",
            duration=120,
            cost=25.0,
            category=ActivityCategory.SIGHTSEEING
        )
        
        day_plan = DayPlan(
            day_number=1,
            activities=[activity],
            transport=[],
            estimated_cost=30.0
        )
        
        # Mismatch between total_days and daily_plans count should fail
        with pytest.raises(ValidationError) as exc_info:
            TripItinerary(
                trip_id="trip_123",
                destination="Paris, France",
                total_days=2,  # Says 2 days
                daily_plans=[day_plan],  # But only 1 day plan
                total_budget=35.0
            )
        assert "must match total days" in str(exc_info.value)
    
    def test_day_numbers_sequential_validation(self):
        """Test that day numbers are sequential starting from 1."""
        activity = Activity(
            name="Test Activity",
            description="Test description",
            duration=120,
            cost=25.0,
            category=ActivityCategory.SIGHTSEEING
        )
        
        day_plan_1 = DayPlan(
            day_number=1,
            activities=[activity],
            transport=[],
            estimated_cost=30.0
        )
        
        day_plan_3 = DayPlan(  # Skipping day 2
            day_number=3,
            activities=[activity],
            transport=[],
            estimated_cost=30.0
        )
        
        # Non-sequential day numbers should fail
        with pytest.raises(ValidationError) as exc_info:
            TripItinerary(
                trip_id="trip_123",
                destination="Paris, France",
                total_days=2,
                daily_plans=[day_plan_1, day_plan_3],
                total_budget=70.0
            )
        assert "sequential starting from 1" in str(exc_info.value)


class TestAPIModels:
    """Test API-specific models."""
    
    def test_api_response(self):
        """Test APIResponse model."""
        response = APIResponse(
            success=True,
            data={"key": "value"},
            message="Success"
        )
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.message == "Success"
    
    def test_error_response(self):
        """Test ErrorResponse model."""
        error = ErrorResponse(
            message="Something went wrong",
            error_code="VALIDATION_ERROR",
            details={"field": "destination"}
        )
        assert error.success is False
        assert error.error is True
        assert error.message == "Something went wrong"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details == {"field": "destination"}
    
    def test_flight_search_params(self):
        """Test FlightSearchParams model."""
        from datetime import date
        params = FlightSearchParams(
            origin="JFK",
            destination="CDG",
            departure_date="2024-06-15",
            return_date="2024-06-22",
            passengers=2
        )
        assert params.origin == "JFK"
        assert params.destination == "CDG"
        assert params.departure_date == date(2024, 6, 15)
        assert params.return_date == date(2024, 6, 22)
        assert params.passengers == 2
        
        # Test validation
        with pytest.raises(ValidationError):
            FlightSearchParams(
                origin="",  # Empty string should fail min_length=1
                destination="CDG",
                departure_date="2024-06-15",
                passengers=1
            )
    
    def test_flight_option(self):
        """Test FlightOption model."""
        flight = FlightOption(
            airline="Air France",
            flight_number="AF83",
            departure_time="14:30",
            arrival_time="16:45",
            duration=495,
            price=650.00,
            stops=0
        )
        assert flight.airline == "Air France"
        assert flight.flight_number == "AF83"
        assert flight.duration == 495
        assert flight.price == 650.00
        assert flight.stops == 0
        
        # Test validation
        with pytest.raises(ValidationError):
            FlightOption(
                airline="Air France",
                flight_number="AF83",
                departure_time="14:30",
                arrival_time="16:45",
                duration=15,  # Too short
                price=650.00,
                stops=0
            )