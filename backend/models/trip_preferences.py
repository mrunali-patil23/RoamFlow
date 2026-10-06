"""
Trip preferences data models for the AI Trip Planner.

This module defines the core data structures for trip planning preferences,
including travel types, budget levels, interests, and the main TripPreferences model.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List


class TravelType(Enum):
    """Enumeration of travel types."""
    SOLO = "Solo"
    FRIENDS = "Friends"
    FAMILY = "Family"
    COUPLE = "Couple"


class BudgetLevel(Enum):
    """Enumeration of budget preference levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Interest(Enum):
    """Enumeration of user interests for trip planning."""
    NATURE = "nature"
    FOOD = "food"
    ADVENTURE = "adventure"
    CULTURE = "culture"
    SHOPPING = "shopping"
    NIGHTLIFE = "nightlife"


@dataclass
class TripPreferences:
    """
    Main data model for trip planning preferences.
    
    Contains all user inputs required for generating a personalized trip plan.
    """
    destination: str
    start_date: date
    end_date: date
    travel_days: int
    travel_type: TravelType
    budget_preference: BudgetLevel
    max_budget_inr: float
    interests: List[Interest]
    
    def __post_init__(self):
        """Validate trip preferences after initialization."""
        from datetime import date
        
        if self.start_date < date.today():
            raise ValueError("Start date must be in the future")
        
        if self.start_date >= self.end_date:
            raise ValueError("End date must be after start date")
        
        if self.travel_days <= 0:
            raise ValueError("Travel days must be positive")
        
        if self.max_budget_inr <= 0:
            raise ValueError("Maximum budget must be positive")
        
        if not self.destination.strip():
            raise ValueError("Destination cannot be empty")