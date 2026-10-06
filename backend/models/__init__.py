"""
Models package for the AI Trip Planner backend.

This package contains all data models and enums used throughout the application.
"""

from .trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
from .travel_data import (
    DateRange, FlightData, HotelData, AttractionData, 
    EventData, WeatherData, TripData
)
from .cost_models import CostBreakdown, DailyCost, BudgetStatus

__all__ = [
    "TripPreferences",
    "TravelType", 
    "BudgetLevel",
    "Interest",
    "DateRange",
    "FlightData",
    "HotelData", 
    "AttractionData",
    "EventData",
    "WeatherData",
    "TripData",
    "CostBreakdown",
    "DailyCost",
    "BudgetStatus"
]