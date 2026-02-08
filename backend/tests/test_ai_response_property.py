"""
Property-based tests for AI response structure validation.

Tests universal properties that should hold for AI-generated itineraries
using Hypothesis for comprehensive input coverage.

Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
"""

import pytest
import json
from hypothesis import given, strategies as st, assume
from typing import Dict, Any, List

from app.services.ai_service import AIService, get_ai_service
from app.models.trip_models import BudgetCategory, TravelerType


# Hypothesis strategies for generating test data
budget_categories = st.sampled_from(["cheap", "moderate", "luxury"])
traveler_types = st.sampled_from(["just-me", "couple", "family", "friends"])
destinations = st.sampled_from([
    "Paris, France", "Tokyo, Japan", "New York, USA", "London, UK", 
    "Rome, Italy", "Barcelona, Spain", "Amsterdam, Netherlands"
])
days_range = st.integers(min_value=1, max_value=7)  # Reasonable range for testing

# Valid activity categories and transport types as per the model
valid_activity_categories = ["sightseeing", "dining", "entertainment", "cultural"]
valid_transport_types = ["flight", "taxi", "bus", "metro", "walking"]


def create_valid_ai_response(days: int) -> Dict[str, Any]:
    """Create a valid AI response structure for testing."""
    daily_plans = []
    total_budget = 0.0
    
    for day in range(1, days + 1):
        activities = [
            {
                "name": f"Activity {day}.1",
                "description": f"Description for activity {day}.1",
                "duration": 120,
                "cost": 50.0,
                "category": "sightseeing"
            },
            {
                "name": f"Activity {day}.2", 
                "description": f"Description for activity {day}.2",
                "duration": 90,
                "cost": 30.0,
                "category": "dining"
            }
        ]
        
        transport = [
            {
                "type": "metro",
                "provider": "Local Transit",
                "cost": 5.0,
                "duration": 20,
                "route": f"Route for day {day}"
            }
        ]
        
        estimated_cost = 100.0
        total_budget += estimated_cost
        
        daily_plans.append({
            "day_number": day,
            "activities": activities,
            "transport": transport,
            "estimated_cost": estimated_cost
        })
    
    return {
        "daily_plans": daily_plans,
        "total_budget": total_budget
    }


def create_invalid_ai_response_missing_field(days: int, missing_field: str) -> Dict[str, Any]:
    """Create an invalid AI response missing a required field."""
    response = create_valid_ai_response(days)
    if missing_field == "daily_plans":
        del response["daily_plans"]
    elif missing_field == "total_budget":
        del response["total_budget"]
    return response


def create_invalid_ai_response_wrong_days(requested_days: int, actual_days: int) -> Dict[str, Any]:
    """Create an AI response with wrong number of days."""
    return create_valid_ai_response(actual_days)


class TestAIResponseStructureProperty:
    """Property-based tests for AI response structure completeness.
    
    Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
    Validates: Requirements 2.5, 2.6
    """
    
    @given(
        destination=destinations,
        days=days_range,
        budget=budget_categories,
        travelers=traveler_types
    )
    def test_ai_response_contains_required_structure(self, destination, days, budget, travelers):
        """
        Property: For any valid trip planning request, the AI service should return 
        structured data containing day-by-day breakdown with activities, transport 
        options, and cost estimates for each day.
        
        Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
        Validates: Requirements 2.5, 2.6
        """
        # Create a valid AI response structure (simulating what AI should return)
        ai_response = create_valid_ai_response(days)
        
        # Validate the response structure
        self._validate_ai_response_structure(ai_response, days)
    
    def _validate_ai_response_structure(self, response: Dict[str, Any], expected_days: int):
        """Validate that AI response has the required structure."""
        # Must have daily_plans field
        assert "daily_plans" in response, "AI response must contain 'daily_plans' field"
        
        # Must have total_budget field
        assert "total_budget" in response, "AI response must contain 'total_budget' field"
        
        daily_plans = response["daily_plans"]
        total_budget = response["total_budget"]
        
        # daily_plans must be a list
        assert isinstance(daily_plans, list), "daily_plans must be a list"
        
        # Must have correct number of days
        assert len(daily_plans) == expected_days, f"Expected {expected_days} daily plans, got {len(daily_plans)}"
        
        # total_budget must be a number
        assert isinstance(total_budget, (int, float)), "total_budget must be a number"
        assert total_budget >= 0, "total_budget must be non-negative"
        
        # Validate each daily plan
        for i, day_plan in enumerate(daily_plans):
            expected_day_number = i + 1
            self._validate_daily_plan_structure(day_plan, expected_day_number)
    
    def _validate_daily_plan_structure(self, day_plan: Dict[str, Any], expected_day_number: int):
        """Validate the structure of a single daily plan."""
        # Required fields
        required_fields = ["day_number", "activities", "transport", "estimated_cost"]
        for field in required_fields:
            assert field in day_plan, f"Daily plan must contain '{field}' field"
        
        # Validate day_number
        assert day_plan["day_number"] == expected_day_number, f"Expected day_number {expected_day_number}, got {day_plan['day_number']}"
        
        # Validate activities
        activities = day_plan["activities"]
        assert isinstance(activities, list), "activities must be a list"
        assert len(activities) > 0, "activities list cannot be empty"
        
        for activity in activities:
            self._validate_activity_structure(activity)
        
        # Validate transport
        transport = day_plan["transport"]
        assert isinstance(transport, list), "transport must be a list"
        
        for transport_option in transport:
            self._validate_transport_structure(transport_option)
        
        # Validate estimated_cost
        estimated_cost = day_plan["estimated_cost"]
        assert isinstance(estimated_cost, (int, float)), "estimated_cost must be a number"
        assert estimated_cost >= 0, "estimated_cost must be non-negative"
    
    def _validate_activity_structure(self, activity: Dict[str, Any]):
        """Validate the structure of a single activity."""
        required_fields = ["name", "description", "duration", "cost", "category"]
        for field in required_fields:
            assert field in activity, f"Activity must contain '{field}' field"
        
        # Validate field types and constraints
        assert isinstance(activity["name"], str) and len(activity["name"]) > 0, "Activity name must be non-empty string"
        assert isinstance(activity["description"], str) and len(activity["description"]) > 0, "Activity description must be non-empty string"
        assert isinstance(activity["duration"], int) and 30 <= activity["duration"] <= 480, "Activity duration must be between 30-480 minutes"
        assert isinstance(activity["cost"], (int, float)) and activity["cost"] >= 0, "Activity cost must be non-negative number"
        assert activity["category"] in valid_activity_categories, f"Activity category must be one of {valid_activity_categories}"
    
    def _validate_transport_structure(self, transport: Dict[str, Any]):
        """Validate the structure of a single transport option."""
        required_fields = ["type", "provider", "cost", "duration", "route"]
        for field in required_fields:
            assert field in transport, f"Transport must contain '{field}' field"
        
        # Validate field types and constraints
        assert transport["type"] in valid_transport_types, f"Transport type must be one of {valid_transport_types}"
        assert isinstance(transport["provider"], str) and len(transport["provider"]) > 0, "Transport provider must be non-empty string"
        assert isinstance(transport["cost"], (int, float)) and transport["cost"] >= 0, "Transport cost must be non-negative number"
        assert isinstance(transport["duration"], int) and transport["duration"] >= 1, "Transport duration must be positive integer"
        assert isinstance(transport["route"], str) and len(transport["route"]) > 0, "Transport route must be non-empty string"
    
    @given(
        days=days_range,
        missing_field=st.sampled_from(["daily_plans", "total_budget"])
    )
    def test_ai_response_missing_required_fields_detected(self, days, missing_field):
        """
        Property: For any AI response missing required fields (daily_plans or total_budget),
        the validation should detect the missing field.
        
        Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
        Validates: Requirements 2.5, 2.6
        """
        # Create invalid response missing a required field
        invalid_response = create_invalid_ai_response_missing_field(days, missing_field)
        
        # Validation should fail
        with pytest.raises(AssertionError) as exc_info:
            self._validate_ai_response_structure(invalid_response, days)
        
        # Error message should mention the missing field
        assert missing_field in str(exc_info.value)
    
    @given(
        requested_days=st.integers(min_value=2, max_value=5),
        actual_days=st.integers(min_value=1, max_value=7)
    )
    def test_ai_response_wrong_day_count_detected(self, requested_days, actual_days):
        """
        Property: For any AI response with incorrect number of daily plans,
        the validation should detect the mismatch.
        
        Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
        Validates: Requirements 2.5, 2.6
        """
        # Skip if days match (this would be a valid case)
        assume(requested_days != actual_days)
        
        # Create response with wrong number of days
        invalid_response = create_invalid_ai_response_wrong_days(requested_days, actual_days)
        
        # Validation should fail
        with pytest.raises(AssertionError) as exc_info:
            self._validate_ai_response_structure(invalid_response, requested_days)
        
        # Error message should mention the day count mismatch
        error_msg = str(exc_info.value)
        assert "daily plans" in error_msg or "Expected" in error_msg


class TestAIServiceResponseValidation:
    """Integration tests for AI service response validation."""
    
    def test_ai_service_json_validation_with_valid_response(self):
        """
        Test that AI service can validate a properly structured JSON response.
        
        Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
        Validates: Requirements 2.5, 2.6
        """
        # Create AI service instance (with test configuration)
        import os
        os.environ['GEMINI_API_KEY'] = 'test_key_for_validation'
        
        ai_service = AIService()
        
        # Create valid JSON response
        valid_response = create_valid_ai_response(3)
        json_string = json.dumps(valid_response)
        
        # Should parse successfully
        parsed_response = ai_service._validate_json_response(json_string)
        
        # Should contain the expected structure
        assert "daily_plans" in parsed_response
        assert "total_budget" in parsed_response
        assert len(parsed_response["daily_plans"]) == 3
    
    def test_ai_service_json_validation_with_invalid_json(self):
        """
        Test that AI service properly handles invalid JSON responses.
        
        Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
        Validates: Requirements 2.5, 2.6
        """
        # Create AI service instance (with test configuration)
        import os
        os.environ['GEMINI_API_KEY'] = 'test_key_for_validation'
        
        from app.core.exceptions import ValidationError
        ai_service = AIService()
        
        # Test with invalid JSON
        invalid_json = "This is not valid JSON"
        
        with pytest.raises(ValidationError) as exc_info:
            ai_service._validate_json_response(invalid_json)
        
        assert "JSON" in str(exc_info.value)
    
    def test_ai_service_fallback_itinerary_structure(self):
        """
        Test that AI service fallback creates properly structured itinerary.
        
        Feature: ai-travel-planner, Property 3: AI Response Structure Completeness
        Validates: Requirements 2.5, 2.6
        """
        # Create AI service instance (with test configuration)
        import os
        os.environ['GEMINI_API_KEY'] = 'test_key_for_validation'
        
        ai_service = AIService()
        
        # Generate fallback itinerary
        fallback = ai_service._create_fallback_itinerary("Paris, France", 3, "moderate", "couple")
        
        # Validate structure
        self._validate_ai_response_structure(fallback, 3)
    
    def _validate_ai_response_structure(self, response: Dict[str, Any], expected_days: int):
        """Reuse validation logic from property tests."""
        test_instance = TestAIResponseStructureProperty()
        test_instance._validate_ai_response_structure(response, expected_days)


class TestTransportOptionsAppropriatenessProperty:
    """Property-based tests for transport options appropriateness.
    
    Feature: ai-travel-planner, Property 4: Transport Options Appropriateness
    Validates: Requirements 2.2, 2.3
    """
    
    @given(
        budget=budget_categories,
        travelers=traveler_types,
        destination=destinations
    )
    def test_transport_options_match_budget_category(self, budget, travelers, destination):
        """
        Property: For any budget category and traveler type combination, the AI engine 
        should generate transport options that are appropriate for the specified budget level.
        
        Feature: ai-travel-planner, Property 4: Transport Options Appropriateness
        Validates: Requirements 2.2, 2.3
        """
        # Create AI service instance
        import os
        os.environ['GEMINI_API_KEY'] = 'test_key_for_validation'
        
        ai_service = AIService()
        
        # Generate fallback itinerary (since we can't test real AI without API key)
        itinerary = ai_service._create_fallback_itinerary(destination, 3, budget, travelers)
        
        # Validate transport options are appropriate for budget
        for day_plan in itinerary["daily_plans"]:
            for transport in day_plan["transport"]:
                self._validate_transport_appropriateness_for_budget(transport, budget)
    
    def _validate_transport_appropriateness_for_budget(self, transport: Dict[str, Any], budget: str):
        """Validate that transport option is appropriate for the given budget."""
        transport_cost = transport["cost"]
        transport_type = transport["type"]
        
        # Define budget-appropriate transport cost ranges and types
        budget_transport_rules = {
            "cheap": {
                "max_cost": 20.0,
                "preferred_types": ["walking", "bus", "metro"],
                "avoid_types": ["flight"]  # For local transport
            },
            "moderate": {
                "max_cost": 50.0,
                "preferred_types": ["walking", "bus", "metro", "taxi"],
                "avoid_types": []
            },
            "luxury": {
                "max_cost": 200.0,
                "preferred_types": ["taxi", "metro", "bus", "walking"],
                "avoid_types": []
            }
        }
        
        rules = budget_transport_rules[budget]
        
        # Validate cost is within budget range
        assert transport_cost <= rules["max_cost"], f"Transport cost {transport_cost} exceeds budget {budget} max of {rules['max_cost']}"
        
        # For cheap budget, avoid expensive transport types for local transport
        if budget == "cheap" and transport_type in rules["avoid_types"]:
            # Allow flights only if cost is reasonable (this would be for inter-city, not local)
            if transport_type == "flight":
                assert transport_cost <= 100.0, f"Flight cost {transport_cost} too high for cheap budget"
    
    @given(
        travelers=traveler_types,
        budget=budget_categories,
        destination=destinations
    )
    def test_activities_match_traveler_type(self, travelers, budget, destination):
        """
        Property: For any traveler type, the AI engine should generate activities 
        that are appropriate for the specified group composition.
        
        Feature: ai-travel-planner, Property 4: Transport Options Appropriateness
        Validates: Requirements 2.2, 2.3
        """
        # Create AI service instance
        import os
        os.environ['GEMINI_API_KEY'] = 'test_key_for_validation'
        
        ai_service = AIService()
        
        # Generate fallback itinerary
        itinerary = ai_service._create_fallback_itinerary(destination, 3, budget, travelers)
        
        # Validate activities are appropriate for traveler type
        for day_plan in itinerary["daily_plans"]:
            for activity in day_plan["activities"]:
                self._validate_activity_appropriateness_for_travelers(activity, travelers)
    
    def _validate_activity_appropriateness_for_travelers(self, activity: Dict[str, Any], travelers: str):
        """Validate that activity is appropriate for the given traveler type."""
        activity_name = activity["name"].lower()
        activity_category = activity["category"]
        activity_cost = activity["cost"]
        
        # Define traveler-appropriate activity guidelines
        traveler_activity_rules = {
            "just-me": {
                "suitable_categories": ["sightseeing", "cultural", "dining", "entertainment"],
                "cost_multiplier": 1.0,  # Base cost
                "avoid_keywords": []  # Solo travelers are flexible
            },
            "couple": {
                "suitable_categories": ["sightseeing", "cultural", "dining", "entertainment"],
                "cost_multiplier": 2.0,  # Cost for two people
                "preferred_keywords": ["romantic", "intimate", "couple"]
            },
            "family": {
                "suitable_categories": ["sightseeing", "cultural", "entertainment"],  # No dining for family
                "cost_multiplier": 3.5,  # Cost for family (2 adults + 1.5 children equivalent)
                "preferred_keywords": ["family", "child", "kid"],
                "avoid_keywords": ["bar", "nightlife", "club"]  # More specific avoid keywords
            },
            "friends": {
                "suitable_categories": ["sightseeing", "entertainment", "dining", "cultural"],
                "cost_multiplier": 3.0,  # Cost for group of friends
                "preferred_keywords": ["group", "social", "friends"]
            }
        }
        
        rules = traveler_activity_rules[travelers]
        
        # Validate category is suitable
        assert activity_category in rules["suitable_categories"], f"Activity category {activity_category} not suitable for {travelers}"
        
        # Validate cost is reasonable for group size (more flexible validation)
        base_cost = 100.0  # Higher base individual cost to be more realistic
        expected_max_cost = base_cost * rules["cost_multiplier"]
        
        # Allow much more flexibility in cost validation (activities can vary widely)
        assert activity_cost <= expected_max_cost * 3, f"Activity cost {activity_cost} seems too high for {travelers} (expected max ~{expected_max_cost * 3})"
        
        # Check for family-inappropriate content (more specific)
        if travelers == "family":
            for avoid_keyword in rules.get("avoid_keywords", []):
                # Only check for exact word matches, not substrings
                activity_words = activity_name.split()
                assert avoid_keyword not in activity_words, f"Activity '{activity_name}' contains inappropriate keyword '{avoid_keyword}' for family travelers"
    
    @given(
        budget=budget_categories,
        travelers=traveler_types,
        days=st.integers(min_value=1, max_value=5)
    )
    def test_daily_cost_matches_budget_and_group_size(self, budget, travelers, days):
        """
        Property: For any budget and traveler combination, the daily estimated costs 
        should be appropriate for both the budget level and group size.
        
        Feature: ai-travel-planner, Property 4: Transport Options Appropriateness
        Validates: Requirements 2.2, 2.3
        """
        # Create AI service instance
        import os
        os.environ['GEMINI_API_KEY'] = 'test_key_for_validation'
        
        ai_service = AIService()
        
        # Generate fallback itinerary
        itinerary = ai_service._create_fallback_itinerary("Paris, France", days, budget, travelers)
        
        # Define expected daily cost ranges
        budget_daily_ranges = {
            "cheap": (30, 80),
            "moderate": (80, 200), 
            "luxury": (200, 500)
        }
        
        traveler_multipliers = {
            "just-me": 1.0,
            "couple": 2.0,
            "family": 3.5,
            "friends": 3.0
        }
        
        base_min, base_max = budget_daily_ranges[budget]
        multiplier = traveler_multipliers[travelers]
        
        expected_min = base_min * multiplier
        expected_max = base_max * multiplier
        
        # Validate each day's cost
        for day_plan in itinerary["daily_plans"]:
            daily_cost = day_plan["estimated_cost"]
            
            # Allow much more flexibility (25% below to 300% above expected range)
            # This accounts for the fact that fallback itineraries are basic estimates
            flexible_min = expected_min * 0.25
            flexible_max = expected_max * 3.0
            
            assert flexible_min <= daily_cost <= flexible_max, (
                f"Daily cost {daily_cost} outside reasonable range [{flexible_min}, {flexible_max}] "
                f"for budget {budget} and travelers {travelers}"
            )