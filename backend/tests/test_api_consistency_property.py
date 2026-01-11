"""
Property-based tests for API response consistency.

**Feature: ai-travel-planner, Property 7: API Response Consistency**
**Validates: Requirements 6.4, 6.5, 6.6**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from fastapi.testclient import TestClient
from fastapi import status
import json
from typing import Dict, Any

# Import the app
from main import app

class TestAPIResponseConsistency:
    """
    Property-based tests for API response consistency.
    Tests that all API endpoints return consistent JSON formatting with appropriate 
    HTTP status codes and error handling.
    """
    
    def get_client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @given(st.text(min_size=1, max_size=100))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property
    def test_health_endpoint_consistency(self, random_query_param):
        """
        Property 7: API Response Consistency - Health endpoint
        
        For any request to the health endpoint, the response should follow 
        consistent JSON formatting with appropriate HTTP status codes.
        
        **Feature: ai-travel-planner, Property 7: API Response Consistency**
        **Validates: Requirements 6.4, 6.5, 6.6**
        """
        client = self.get_client()
        
        # Test basic health endpoint
        response = client.get("/api/v1/health")
        
        # Should always return 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Should return valid JSON
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have consistent structure
        assert "status" in data
        assert "service" in data
        assert "version" in data
        
        # Status should be healthy
        assert data["status"] == "healthy"
        assert data["service"] == "ai-travel-planner-api"
        assert data["version"] == "1.0.0"
        
        # Should have security headers
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-request-id" in response.headers
    
    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=0,
            max_size=5
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property
    def test_invalid_endpoint_error_consistency(self, query_params):
        """
        Property 7: API Response Consistency - Error responses
        
        For any request to non-existent endpoints, the error response should 
        follow consistent JSON formatting with appropriate HTTP status codes.
        
        **Feature: ai-travel-planner, Property 7: API Response Consistency**
        **Validates: Requirements 6.6**
        """
        client = self.get_client()
        
        # Generate a random invalid endpoint path
        invalid_path = "/api/v1/nonexistent-endpoint"
        
        response = client.get(invalid_path, params=query_params)
        
        # Should return 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Should return valid JSON error response
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have consistent error structure
        assert "success" in data
        assert "error" in data
        assert "message" in data
        assert "error_code" in data
        
        # Error response structure validation
        assert data["success"] is False
        assert data["error"] is True
        assert isinstance(data["message"], str)
        assert isinstance(data["error_code"], str)
        
        # Should have security headers
        assert "x-content-type-options" in response.headers
        assert "x-request-id" in response.headers
    
    @given(
        st.dictionaries(
            st.sampled_from(["destination", "days", "budget", "travelers"]),
            st.one_of(
                st.text(min_size=0, max_size=100),
                st.integers(min_value=-100, max_value=100),
                st.none()
            ),
            min_size=0,
            max_size=4
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property
    def test_trip_planning_validation_consistency(self, trip_data):
        """
        Property 7: API Response Consistency - Validation errors
        
        For any invalid trip planning request, the validation error response 
        should follow consistent JSON formatting with appropriate HTTP status codes.
        
        **Feature: ai-travel-planner, Property 7: API Response Consistency**
        **Validates: Requirements 6.4, 6.5, 6.6**
        """
        client = self.get_client()
        
        # Assume we have some invalid data (missing required fields or invalid values)
        assume(not self._is_valid_trip_request(trip_data))
        
        response = client.post("/api/v1/trips/plan-trip", json=trip_data)
        
        # Should return validation error status
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,  # Pydantic validation error
            status.HTTP_400_BAD_REQUEST,           # Custom validation error
            status.HTTP_500_INTERNAL_SERVER_ERROR  # Service not implemented yet
        ]
        
        # Should return valid JSON
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have consistent error structure
        assert "success" in data
        assert "error" in data
        assert "message" in data
        assert "error_code" in data
        
        # Error response validation
        assert data["success"] is False
        assert data["error"] is True
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
        assert isinstance(data["error_code"], str)
        
        # Should have security headers
        assert "x-content-type-options" in response.headers
        assert "x-request-id" in response.headers
    
    @given(
        st.dictionaries(
            st.sampled_from(["origin", "destination", "departure_date", "passengers"]),
            st.one_of(
                st.text(min_size=0, max_size=50),
                st.integers(min_value=-10, max_value=20),
                st.dates().map(str),
                st.none()
            ),
            min_size=0,
            max_size=4
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property
    def test_transport_endpoints_consistency(self, transport_params):
        """
        Property 7: API Response Consistency - Transport endpoints
        
        For any request to transport endpoints, the response should follow 
        consistent JSON formatting with appropriate HTTP status codes.
        
        **Feature: ai-travel-planner, Property 7: API Response Consistency**
        **Validates: Requirements 6.4, 6.5, 6.6**
        """
        client = self.get_client()
        
        # Test flights endpoint
        response = client.get("/api/v1/transport/flights", params=transport_params)
        
        # Should return appropriate status code
        assert response.status_code in [
            status.HTTP_200_OK,                    # Valid request
            status.HTTP_422_UNPROCESSABLE_ENTITY,  # Validation error
            status.HTTP_400_BAD_REQUEST,           # Bad request
            status.HTTP_500_INTERNAL_SERVER_ERROR  # Service not implemented
        ]
        
        # Should return valid JSON
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have consistent response structure
        if response.status_code == status.HTTP_200_OK:
            # Success response structure
            assert "success" in data
            assert "data" in data
            assert "message" in data
            assert data["success"] is True
        else:
            # Error response structure
            assert "success" in data
            assert "error" in data
            assert "message" in data
            assert "error_code" in data
            assert data["success"] is False
            assert data["error"] is True
        
        # Should have security headers
        assert "x-content-type-options" in response.headers
        assert "x-request-id" in response.headers
    
    def _is_valid_trip_request(self, data: Dict[str, Any]) -> bool:
        """
        Helper method to check if trip request data is valid.
        Used to filter out valid requests in property tests.
        """
        required_fields = ["destination", "days", "budget", "travelers"]
        
        # Check if all required fields are present
        if not all(field in data for field in required_fields):
            return False
        
        # Check field types and values
        if not isinstance(data.get("destination"), str) or len(data["destination"]) == 0:
            return False
        
        if not isinstance(data.get("days"), int) or data["days"] < 1 or data["days"] > 30:
            return False
        
        if data.get("budget") not in ["cheap", "moderate", "luxury"]:
            return False
        
        if data.get("travelers") not in ["just-me", "couple", "family", "friends"]:
            return False
        
        return True
    
    @pytest.mark.property
    def test_root_endpoint_consistency(self):
        """
        Property 7: API Response Consistency - Root endpoint
        
        The root endpoint should always return consistent JSON formatting 
        with appropriate HTTP status codes.
        
        **Feature: ai-travel-planner, Property 7: API Response Consistency**
        **Validates: Requirements 6.4, 6.5**
        """
        client = self.get_client()
        
        response = client.get("/")
        
        # Should always return 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Should return valid JSON
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have consistent structure
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        
        # Should have expected values
        assert data["message"] == "AI Travel Planner API is running"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/api/docs"
        
        # Should have security headers
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-request-id" in response.headers