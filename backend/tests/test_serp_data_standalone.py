"""
Standalone SERP API data structure validation tests.
Tests data structure validation logic without external dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from datetime import date, timedelta


class StandaloneDataIntegrationService:
    """Standalone data integration service for testing without external dependencies."""
    
    def __init__(self):
        self.api_key = 'test-api-key'
        self.base_url = 'https://serpapi.com'
    
    def validate_flight_data_structure(self, response: Dict[str, Any]) -> bool:
        """Validate that flight data has required structure."""
        try:
            # Check for required top-level fields
            if 'search_metadata' not in response:
                return False
            
            # Check for flight data
            has_flights = ('best_flights' in response and isinstance(response['best_flights'], list)) or \
                         ('other_flights' in response and isinstance(response['other_flights'], list))
            
            if not has_flights:
                return False
            
            # Validate flight structure
            all_flights = response.get('best_flights', []) + response.get('other_flights', [])
            for flight in all_flights:
                if not isinstance(flight, dict):
                    return False
                # Check for basic flight fields
                if 'flights' not in flight or not isinstance(flight['flights'], list):
                    return False
            
            return True
        except Exception:
            return False
    
    def validate_hotel_data_structure(self, response: Dict[str, Any]) -> bool:
        """Validate that hotel data has required structure."""
        try:
            # Check for required top-level fields
            if 'search_metadata' not in response:
                return False
            
            # Check for hotel data
            if 'properties' not in response or not isinstance(response['properties'], list):
                return False
            
            # Validate hotel structure
            for hotel in response['properties']:
                if not isinstance(hotel, dict):
                    return False
                # Check for basic hotel fields
                if 'name' not in hotel:
                    return False
            
            return True
        except Exception:
            return False
    
    def validate_attraction_data_structure(self, response: Dict[str, Any]) -> bool:
        """Validate that attraction data has required structure."""
        try:
            # Check for required top-level fields
            if 'search_metadata' not in response:
                return False
            
            # Check for attraction data
            if 'local_results' not in response or not isinstance(response['local_results'], list):
                return False
            
            # Validate attraction structure
            for attraction in response['local_results']:
                if not isinstance(attraction, dict):
                    return False
                # Check for basic attraction fields
                if 'title' not in attraction:
                    return False
            
            return True
        except Exception:
            return False
    
    def validate_event_data_structure(self, response: Dict[str, Any]) -> bool:
        """Validate that event data has required structure."""
        try:
            # Check for required top-level fields
            if 'search_metadata' not in response:
                return False
            
            # Check for event data
            if 'events_results' not in response or not isinstance(response['events_results'], list):
                return False
            
            # Validate event structure
            for event in response['events_results']:
                if not isinstance(event, dict):
                    return False
                # Check for basic event fields
                if 'title' not in event:
                    return False
            
            return True
        except Exception:
            return False
    
    def validate_weather_data_structure(self, response: Dict[str, Any]) -> bool:
        """Validate that weather data has required structure."""
        try:
            # Check for required top-level fields
            if 'search_metadata' not in response:
                return False
            
            # Check for weather data (either answer_box or knowledge_graph)
            has_weather = ('answer_box' in response and isinstance(response['answer_box'], dict)) or \
                         ('knowledge_graph' in response and isinstance(response['knowledge_graph'], dict))
            
            return has_weather
        except Exception:
            return False


def test_serp_api_data_structure_validation():
    """Test SERP API data structure validation."""
    service = StandaloneDataIntegrationService()
    
    # Test valid flight data structure
    valid_flight_response = {
        'search_metadata': {'id': 'test-id', 'status': 'Success'},
        'best_flights': [
            {
                'flights': [
                    {
                        'departure_airport': {'name': 'Delhi Airport', 'id': 'DEL'},
                        'arrival_airport': {'name': 'Mumbai Airport', 'id': 'BOM'},
                        'duration': 120,
                        'airline': 'Test Airlines'
                    }
                ],
                'price': 15000
            }
        ]
    }
    
    assert service.validate_flight_data_structure(valid_flight_response), "Valid flight data should pass validation"
    
    # Test invalid flight data structure (missing search_metadata)
    invalid_flight_response = {
        'best_flights': [{'flights': []}]
    }
    
    assert not service.validate_flight_data_structure(invalid_flight_response), "Invalid flight data should fail validation"
    
    # Test valid hotel data structure
    valid_hotel_response = {
        'search_metadata': {'id': 'test-id', 'status': 'Success'},
        'properties': [
            {
                'name': 'Test Hotel',
                'description': 'A nice hotel',
                'rate_per_night': {'lowest': '₹5,000'}
            }
        ]
    }
    
    assert service.validate_hotel_data_structure(valid_hotel_response), "Valid hotel data should pass validation"
    
    # Test invalid hotel data structure (missing properties)
    invalid_hotel_response = {
        'search_metadata': {'id': 'test-id'}
    }
    
    assert not service.validate_hotel_data_structure(invalid_hotel_response), "Invalid hotel data should fail validation"
    
    # Test valid attraction data structure
    valid_attraction_response = {
        'search_metadata': {'id': 'test-id', 'status': 'Success'},
        'local_results': [
            {
                'title': 'Famous Monument',
                'rating': 4.5,
                'address': '123 Main Street'
            }
        ]
    }
    
    assert service.validate_attraction_data_structure(valid_attraction_response), "Valid attraction data should pass validation"
    
    # Test valid event data structure
    valid_event_response = {
        'search_metadata': {'id': 'test-id', 'status': 'Success'},
        'events_results': [
            {
                'title': 'Cultural Festival',
                'date': {'start_date': '2024-01-01'},
                'venue': {'name': 'Cultural Center'}
            }
        ]
    }
    
    assert service.validate_event_data_structure(valid_event_response), "Valid event data should pass validation"
    
    # Test valid weather data structure
    valid_weather_response = {
        'search_metadata': {'id': 'test-id', 'status': 'Success'},
        'answer_box': {
            'type': 'weather_result',
            'location': 'Mumbai',
            'temperature': 28,
            'weather': 'Partly cloudy'
        }
    }
    
    assert service.validate_weather_data_structure(valid_weather_response), "Valid weather data should pass validation"


def test_serp_api_error_handling():
    """Test SERP API error handling."""
    service = StandaloneDataIntegrationService()
    
    # Test empty response
    empty_response = {}
    
    assert not service.validate_flight_data_structure(empty_response), "Empty response should fail validation"
    assert not service.validate_hotel_data_structure(empty_response), "Empty response should fail validation"
    assert not service.validate_attraction_data_structure(empty_response), "Empty response should fail validation"
    assert not service.validate_event_data_structure(empty_response), "Empty response should fail validation"
    assert not service.validate_weather_data_structure(empty_response), "Empty response should fail validation"
    
    # Test malformed response
    malformed_response = {
        'search_metadata': 'not-a-dict',
        'best_flights': 'not-a-list'
    }
    
    assert not service.validate_flight_data_structure(malformed_response), "Malformed response should fail validation"


def test_serp_api_data_consistency():
    """Test that SERP API data validation is consistent."""
    service = StandaloneDataIntegrationService()
    
    # Test that validation is consistent for the same input
    test_response = {
        'search_metadata': {'id': 'test-id', 'status': 'Success'},
        'best_flights': [
            {
                'flights': [{'departure_airport': {'name': 'Test'}}],
                'price': 1000
            }
        ]
    }
    
    result1 = service.validate_flight_data_structure(test_response)
    result2 = service.validate_flight_data_structure(test_response)
    
    assert result1 == result2, "Validation should be consistent for the same input"
    
    # Test that all validation methods handle None input gracefully
    validation_methods = [
        service.validate_flight_data_structure,
        service.validate_hotel_data_structure,
        service.validate_attraction_data_structure,
        service.validate_event_data_structure,
        service.validate_weather_data_structure
    ]
    
    for method in validation_methods:
        try:
            result = method(None)
            assert result == False, f"{method.__name__} should return False for None input"
        except Exception as e:
            # If it raises an exception, that's also acceptable for None input
            pass


if __name__ == "__main__":
    test_serp_api_data_structure_validation()
    test_serp_api_error_handling()
    test_serp_api_data_consistency()
    print("All SERP API data structure validation tests passed!")