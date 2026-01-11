"""
Trip-related Pydantic models for the AI Travel Planner.

This module defines the core data models for trip planning, including
trip requests, itineraries, daily plans, activities, and transport options.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class BudgetCategory(str, Enum):
    """Budget category enumeration."""
    CHEAP = "cheap"
    MODERATE = "moderate"
    LUXURY = "luxury"


class TravelerType(str, Enum):
    """Traveler type enumeration."""
    JUST_ME = "just-me"
    COUPLE = "couple"
    FAMILY = "family"
    FRIENDS = "friends"


class ActivityCategory(str, Enum):
    """Activity category enumeration."""
    SIGHTSEEING = "sightseeing"
    DINING = "dining"
    ENTERTAINMENT = "entertainment"
    CULTURAL = "cultural"


class TransportType(str, Enum):
    """Transport type enumeration."""
    FLIGHT = "flight"
    TAXI = "taxi"
    BUS = "bus"
    METRO = "metro"
    WALKING = "walking"


class TripRequest(BaseModel):
    """Model for trip planning request data."""
    destination: str = Field(..., min_length=1, max_length=100, description="Travel destination")
    days: int = Field(..., ge=1, le=30, description="Number of days for the trip")
    budget: BudgetCategory = Field(..., description="Budget category for the trip")
    travelers: TravelerType = Field(..., description="Type of travelers")

    @validator('destination')
    def validate_destination(cls, v):
        """Validate destination is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError('Destination cannot be empty')
        return v.strip()

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "destination": "Paris, France",
                "days": 5,
                "budget": "moderate",
                "travelers": "couple"
            }
        }


class Activity(BaseModel):
    """Model for individual activities within a day plan."""
    name: str = Field(..., min_length=1, max_length=200, description="Activity name")
    description: str = Field(..., min_length=1, max_length=1000, description="Activity description")
    duration: int = Field(..., ge=30, le=480, description="Duration in minutes")
    cost: float = Field(..., ge=0, description="Estimated cost in USD")
    category: ActivityCategory = Field(..., description="Activity category")

    @validator('name', 'description')
    def validate_not_empty(cls, v):
        """Validate fields are not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "Visit Eiffel Tower",
                "description": "Iconic iron lattice tower and symbol of Paris",
                "duration": 120,
                "cost": 25.0,
                "category": "sightseeing"
            }
        }


class TransportOption(BaseModel):
    """Model for transport options."""
    type: TransportType = Field(..., description="Type of transport")
    provider: str = Field(..., min_length=1, max_length=100, description="Transport provider")
    cost: float = Field(..., ge=0, description="Cost in USD")
    duration: int = Field(..., ge=1, description="Duration in minutes")
    route: str = Field(..., min_length=1, max_length=500, description="Route description")

    @validator('provider', 'route')
    def validate_not_empty(cls, v):
        """Validate fields are not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "type": "metro",
                "provider": "RATP",
                "cost": 1.90,
                "duration": 25,
                "route": "Line 6 from Trocadéro to Eiffel Tower"
            }
        }


class DayPlan(BaseModel):
    """Model for a single day's plan within an itinerary."""
    day_number: int = Field(..., ge=1, description="Day number in the trip")
    activities: List[Activity] = Field(..., min_items=1, description="List of activities for the day")
    transport: List[TransportOption] = Field(default_factory=list, description="Transport options for the day")
    estimated_cost: float = Field(..., ge=0, description="Total estimated cost for the day")

    @validator('estimated_cost')
    def validate_cost_matches_activities(cls, v, values):
        """Validate that estimated cost is reasonable based on activities and transport."""
        if 'activities' in values and 'transport' in values:
            activity_cost = sum(activity.cost for activity in values['activities'])
            transport_cost = sum(transport.cost for transport in values['transport'])
            total_cost = activity_cost + transport_cost
            
            # Allow some variance for additional costs (meals, tips, etc.)
            if v < total_cost * 0.8 or v > total_cost * 2.0:
                raise ValueError(f'Estimated cost {v} seems unreasonable compared to activity/transport costs {total_cost}')
        
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "day_number": 1,
                "activities": [
                    {
                        "name": "Visit Eiffel Tower",
                        "description": "Iconic iron lattice tower and symbol of Paris",
                        "duration": 120,
                        "cost": 25.0,
                        "category": "sightseeing"
                    }
                ],
                "transport": [
                    {
                        "type": "metro",
                        "provider": "RATP",
                        "cost": 1.90,
                        "duration": 25,
                        "route": "Line 6 from Trocadéro to Eiffel Tower"
                    }
                ],
                "estimated_cost": 45.0
            }
        }


class TripItinerary(BaseModel):
    """Model for complete trip itinerary."""
    trip_id: str = Field(..., min_length=1, description="Unique trip identifier")
    destination: str = Field(..., min_length=1, description="Trip destination")
    total_days: int = Field(..., ge=1, le=30, description="Total number of days")
    daily_plans: List[DayPlan] = Field(..., min_items=1, description="Daily plans for the trip")
    total_budget: float = Field(..., ge=0, description="Total estimated budget")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    @validator('daily_plans')
    def validate_daily_plans_count(cls, v, values):
        """Validate that number of daily plans matches total days."""
        if 'total_days' in values and len(v) != values['total_days']:
            raise ValueError(f'Number of daily plans ({len(v)}) must match total days ({values["total_days"]})')
        return v

    @validator('daily_plans')
    def validate_day_numbers_sequential(cls, v):
        """Validate that day numbers are sequential starting from 1."""
        expected_days = list(range(1, len(v) + 1))
        actual_days = [plan.day_number for plan in v]
        if actual_days != expected_days:
            raise ValueError(f'Day numbers must be sequential starting from 1. Expected: {expected_days}, Got: {actual_days}')
        return v

    @validator('total_budget')
    def validate_total_budget_matches_daily_costs(cls, v, values):
        """Validate that total budget is reasonable based on daily costs."""
        if 'daily_plans' in values:
            daily_total = sum(plan.estimated_cost for plan in values['daily_plans'])
            # Allow some variance for additional costs
            if v < daily_total * 0.8 or v > daily_total * 1.5:
                raise ValueError(f'Total budget {v} seems unreasonable compared to daily costs {daily_total}')
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "trip_id": "trip_123456",
                "destination": "Paris, France",
                "total_days": 3,
                "daily_plans": [
                    {
                        "day_number": 1,
                        "activities": [
                            {
                                "name": "Visit Eiffel Tower",
                                "description": "Iconic iron lattice tower and symbol of Paris",
                                "duration": 120,
                                "cost": 25.0,
                                "category": "sightseeing"
                            }
                        ],
                        "transport": [
                            {
                                "type": "metro",
                                "provider": "RATP",
                                "cost": 1.90,
                                "duration": 25,
                                "route": "Line 6 from Trocadéro to Eiffel Tower"
                            }
                        ],
                        "estimated_cost": 45.0
                    }
                ],
                "total_budget": 135.0,
                "created_at": "2024-01-01T12:00:00Z"
            }
        }