"""
Property-based tests for transport service data completeness.

**Feature: ai-travel-planner, Property 5: Transport Data Completeness**
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import date, timedelta
import asyncio
from app.services.transport_service import TransportService
from app.models.api_models import FlightSearchParams, TransportRequest


# Strategies for generating test data
@st.composite
def flight_search_params(draw):
    """Generate valid FlightSearchParams for testing."""
    # Common airport codes
    airports = ["JFK", "LAX", "LHR", "CDG", "NRT", "DXB", "SYD", "FRA", "AMS", "BCN"]
    
    origin = draw(st.sampled_from(airports))
    destination = draw(st.sampled_from([a for a in airports if a != origin]))
    
    # Generate dates within reasonable range
    base_date = date.today() + timedelta(days=1)
    departure_date = draw(st.dates(
        min_value=base_date,
        max_value=base_date + timedelta(days=365)
    ))
    
    # Optional return date (50% chance)
    return_date = None
    if draw(st.booleans()):
        return_date = draw(st.dates(
            min_value=departure_date + timedelta(days=1),
            max_value=departure_date + timedelta(days=30)
        ))
    
    passengers = draw(st.integers(min_value=1, max_value=9))
    
    return FlightSearchParams(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        passengers=passengers
    )


@st.composite
def transport_request(draw):
    """Generate valid TransportRequest for testing."""
    # Common cities and locations
    locations = [
        "New York, NY, USA",
        "London, UK",
        "Paris, France",
        "Tokyo, Japan",
        "Berlin, Germany",
        "Sydney, Australia",
        "Madrid, Spain",
        "Rome, Italy",
        "Barcelona, Spain",
        "Amsterdam, Netherlands"
    ]
    
    location = draw(st.sampled_from(locations))
    
    # Optional transport type filter
    transport_types = ["taxi", "metro", "bus", "rideshare", None]
    transport_type = draw(st.sampled_from(transport_types))
    
    return TransportRequest(
        location=location,
        transport_type=transport_type
    )


class TestTransportDataCompleteness:
    """Test transport service data completeness properties."""
    
    @given(flight_search_params())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @pytest.mark.asyncio
    async def test_flight_search_returns_complete_data(self, params):
        """
        Property: For any valid flight search parameters, the service should return
        complete flight data with all required fields.
        
        **Feature: ai-travel-planner, Property 5: Transport Data Completeness**
        **Validates: Requirements 3.1, 3.3**
        """
        transport_service = TransportService()
        
        # Execute flight search
        flights = await transport_service.search_flights(params)
        
        # Verify response structure
        assert isinstance(flights, list), "Flight search should return a list"
        assert len(flights) > 0, "Flight search should return at least one option"
        
        # Verify each flight has complete data
        for flight in flights:
            assert isinstance(flight, dict), "Each flight should be a dictionary"
            
            # Required fields for flight data
            required_fields = [
                "airline", "flight_number", "departure_time", "arrival_time",
                "duration", "price", "stops", "currency"
            ]
            
            for field in required_fields:
                assert field in flight, f"Flight data missing required field: {field}"
                assert flight[field] is not None, f"Flight field {field} should not be None"
            
            # Verify data types and constraints
            assert isinstance(flight["airline"], str), "Airline should be string"
            assert len(flight["airline"]) > 0, "Airline should not be empty"
            
            assert isinstance(flight["flight_number"], str), "Flight number should be string"
            assert len(flight["flight_number"]) > 0, "Flight number should not be empty"
            
            assert isinstance(flight["price"], (int, float)), "Price should be numeric"
            assert flight["price"] > 0, "Price should be positive"
            
            assert isinstance(flight["stops"], int), "Stops should be integer"
            assert flight["stops"] >= 0, "Stops should be non-negative"
            
            assert isinstance(flight["duration"], int), "Duration should be integer"
            assert flight["duration"] > 0, "Duration should be positive"
            
            assert isinstance(flight["currency"], str), "Currency should be string"
            assert len(flight["currency"]) >= 3, "Currency should be valid code"
    
    @given(transport_request())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @pytest.mark.asyncio
    async def test_local_transport_returns_complete_data(self, request):
        """
        Property: For any valid transport request, the service should return
        complete local transport options with all required fields.
        
        **Feature: ai-travel-planner, Property 5: Transport Data Completeness**
        **Validates: Requirements 3.2, 3.4**
        """
        transport_service = TransportService()
        
        # Execute local transport search
        transport_options = await transport_service.get_local_transport(request)
        
        # Verify response structure
        assert isinstance(transport_options, list), "Transport search should return a list"
        assert len(transport_options) > 0, "Transport search should return at least one option"
        
        # Verify each transport option has complete data
        for option in transport_options:
            assert isinstance(option, dict), "Each transport option should be a dictionary"
            
            # Required fields for transport data
            required_fields = ["type", "provider", "currency", "availability"]
            
            for field in required_fields:
                assert field in option, f"Transport option missing required field: {field}"
                assert option[field] is not None, f"Transport field {field} should not be None"
            
            # Verify data types
            assert isinstance(option["type"], str), "Transport type should be string"
            assert len(option["type"]) > 0, "Transport type should not be empty"
            
            assert isinstance(option["provider"], str), "Provider should be string"
            assert len(option["provider"]) > 0, "Provider should not be empty"
            
            assert isinstance(option["currency"], str), "Currency should be string"
            assert len(option["currency"]) >= 3, "Currency should be valid code"
            
            assert isinstance(option["availability"], str), "Availability should be string"
            assert len(option["availability"]) > 0, "Availability should not be empty"
            
            # Verify pricing fields based on transport type
            transport_type = option["type"]
            
            if transport_type in ["taxi", "rideshare"]:
                # Should have base_fare and per_km
                assert "base_fare" in option, f"{transport_type} should have base_fare"
                assert "per_km" in option, f"{transport_type} should have per_km"
                assert isinstance(option["base_fare"], (int, float)), "Base fare should be numeric"
                assert isinstance(option["per_km"], (int, float)), "Per km rate should be numeric"
                assert option["base_fare"] > 0, "Base fare should be positive"
                assert option["per_km"] > 0, "Per km rate should be positive"
            
            elif transport_type in ["metro", "bus"]:
                # Should have cost_per_ride and day_pass
                assert "cost_per_ride" in option, f"{transport_type} should have cost_per_ride"
                assert "day_pass" in option, f"{transport_type} should have day_pass"
                assert isinstance(option["cost_per_ride"], (int, float)), "Cost per ride should be numeric"
                assert isinstance(option["day_pass"], (int, float)), "Day pass should be numeric"
                assert option["cost_per_ride"] > 0, "Cost per ride should be positive"
                assert option["day_pass"] > 0, "Day pass should be positive"
    
    @given(transport_request())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @pytest.mark.asyncio
    async def test_transport_includes_essential_types(self, request):
        """
        Property: For any location, transport options should include essential
        transport types (taxi should always be available).
        
        **Feature: ai-travel-planner, Property 5: Transport Data Completeness**
        **Validates: Requirements 3.2, 3.4**
        """
        transport_service = TransportService()
        
        # Execute local transport search
        transport_options = await transport_service.get_local_transport(request)
        
        # Extract transport types
        transport_types = [option["type"] for option in transport_options]
        
        # Taxi should always be available
        assert "taxi" in transport_types, "Taxi should always be available as transport option"
        
        # Should have multiple transport options
        assert len(transport_types) >= 2, "Should provide multiple transport options"
        
        # All types should be valid
        valid_types = ["taxi", "metro", "bus", "rideshare", "walking"]
        for transport_type in transport_types:
            assert transport_type in valid_types, f"Invalid transport type: {transport_type}"
    
    @given(flight_search_params())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5)
    @pytest.mark.asyncio
    async def test_flight_search_handles_api_unavailability(self, params):
        """
        Property: Flight search should provide reasonable mock data when external
        APIs are unavailable, maintaining data completeness.
        
        **Feature: ai-travel-planner, Property 5: Transport Data Completeness**
        **Validates: Requirements 3.3**
        """
        transport_service = TransportService()
        
        # Force use of mock data by setting client to None
        original_client = transport_service.amadeus_client
        transport_service.amadeus_client = None
        
        try:
            # Execute flight search with mock data
            flights = await transport_service.search_flights(params)
            
            # Verify mock data is complete and reasonable
            assert isinstance(flights, list), "Mock flight search should return a list"
            assert len(flights) > 0, "Mock flight search should return options"
            
            for flight in flights:
                # Verify all required fields are present
                required_fields = [
                    "airline", "flight_number", "departure_time", "arrival_time",
                    "duration", "price", "stops", "currency"
                ]
                
                for field in required_fields:
                    assert field in flight, f"Mock flight missing field: {field}"
                    assert flight[field] is not None, f"Mock flight field {field} is None"
                
                # Verify reasonable values
                assert flight["price"] > 0, "Mock flight price should be positive"
                assert flight["duration"] > 0, "Mock flight duration should be positive"
                assert flight["stops"] >= 0, "Mock flight stops should be non-negative"
                
        finally:
            # Restore original client
            transport_service.amadeus_client = original_client
    
    @given(transport_request())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5)
    @pytest.mark.asyncio
    async def test_transport_search_handles_api_unavailability(self, request):
        """
        Property: Transport search should provide reasonable mock data when external
        APIs are unavailable, maintaining data completeness.
        
        **Feature: ai-travel-planner, Property 5: Transport Data Completeness**
        **Validates: Requirements 3.3**
        """
        transport_service = TransportService()
        
        # Force use of mock data by setting client to None
        original_client = transport_service.gmaps_client
        transport_service.gmaps_client = None
        
        try:
            # Execute transport search with mock data
            transport_options = await transport_service.get_local_transport(request)
            
            # Verify mock data is complete and reasonable
            assert isinstance(transport_options, list), "Mock transport search should return a list"
            assert len(transport_options) > 0, "Mock transport search should return options"
            
            for option in transport_options:
                # Verify all required fields are present
                required_fields = ["type", "provider", "currency", "availability"]
                
                for field in required_fields:
                    assert field in option, f"Mock transport missing field: {field}"
                    assert option[field] is not None, f"Mock transport field {field} is None"
                
                # Verify reasonable pricing data exists
                transport_type = option["type"]
                if transport_type in ["taxi", "rideshare"]:
                    assert "base_fare" in option, f"Mock {transport_type} missing base_fare"
                    assert "per_km" in option, f"Mock {transport_type} missing per_km"
                    assert option["base_fare"] > 0, "Mock base fare should be positive"
                    assert option["per_km"] > 0, "Mock per km rate should be positive"
                elif transport_type in ["metro", "bus"]:
                    assert "cost_per_ride" in option, f"Mock {transport_type} missing cost_per_ride"
                    assert "day_pass" in option, f"Mock {transport_type} missing day_pass"
                    assert option["cost_per_ride"] > 0, "Mock cost per ride should be positive"
                    assert option["day_pass"] > 0, "Mock day pass should be positive"
                
        finally:
            # Restore original client
            transport_service.gmaps_client = original_client
    
    @given(st.lists(flight_search_params(), min_size=1, max_size=2))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5)
    @pytest.mark.asyncio
    async def test_consistent_data_format_across_requests(self, params_list):
        """
        Property: All flight search responses should have consistent data formatting
        regardless of input parameters.
        
        **Feature: ai-travel-planner, Property 5: Transport Data Completeness**
        **Validates: Requirements 3.4**
        """
        transport_service = TransportService()
        all_flights = []
        
        # Execute multiple flight searches
        for params in params_list:
            flights = await transport_service.search_flights(params)
            all_flights.extend(flights)
        
        if not all_flights:
            return  # Skip if no flights returned
        
        # Verify consistent structure across all flights
        first_flight_keys = set(all_flights[0].keys())
        
        for flight in all_flights[1:]:
            flight_keys = set(flight.keys())
            assert flight_keys == first_flight_keys, "All flights should have consistent field structure"
            
            # Verify consistent data types
            for key in first_flight_keys:
                first_type = type(all_flights[0][key])
                current_type = type(flight[key])
                assert current_type == first_type, f"Field {key} should have consistent type across flights"