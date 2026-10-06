"""
Itinerary models for the AI Trip Planner.

This module defines data structures for itineraries, day plans, activities,
and weather information as specified in the design document.
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Dict, Any, Optional
from enum import Enum


class ActivityType(Enum):
    """Types of activities in an itinerary."""
    ATTRACTION = "attraction"
    EVENT = "event"
    MEAL = "meal"
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    FREE_TIME = "free_time"


@dataclass
class WeatherInfo:
    """Weather information for a specific day."""
    date: date
    temperature_high: Optional[float] = None
    temperature_low: Optional[float] = None
    condition: str = "Unknown"
    description: str = ""
    humidity: Optional[int] = None
    precipitation_chance: Optional[int] = None
    
    @classmethod
    def from_weather_data(cls, weather_data: Dict[str, Any], target_date: date) -> 'WeatherInfo':
        """Create WeatherInfo from weather data for a specific date."""
        # Extract weather info for the target date
        forecast_data = {}
        
        # Look for forecast data matching the target date
        if 'forecast' in weather_data:
            for forecast in weather_data['forecast']:
                forecast_date_str = forecast.get('date', '')
                if forecast_date_str and target_date.strftime('%Y-%m-%d') in forecast_date_str:
                    forecast_data = forecast
                    break
        
        # Fallback to current weather if no forecast found
        if not forecast_data and 'current_weather' in weather_data:
            forecast_data = weather_data['current_weather']
        
        return cls(
            date=target_date,
            temperature_high=forecast_data.get('high', forecast_data.get('temperature')),
            temperature_low=forecast_data.get('low'),
            condition=forecast_data.get('weather', forecast_data.get('condition', 'Unknown')),
            description=forecast_data.get('description', ''),
            humidity=forecast_data.get('humidity'),
            precipitation_chance=forecast_data.get('precipitation_chance', forecast_data.get('rain'))
        )


@dataclass
class Activity:
    """Individual activity in a day plan."""
    name: str
    activity_type: ActivityType
    description: str
    duration_hours: float
    cost_inr: float
    location: str = ""
    rating: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    booking_required: bool = False
    source_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_attraction_data(cls, attraction: Dict[str, Any], ai_description: str = "") -> 'Activity':
        """Create Activity from attraction data."""
        # Convert rating to float if it's a string
        rating = attraction.get('rating')
        if rating is not None:
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                rating = None
        
        return cls(
            name=attraction.get('title', 'Unknown Attraction'),
            activity_type=ActivityType.ATTRACTION,
            description=ai_description or attraction.get('snippet', 'A local attraction'),
            duration_hours=2.0,  # Default 2 hours for attractions
            cost_inr=attraction.get('price_inr', 200.0),  # Default ₹200
            location=attraction.get('address', ''),
            rating=rating,
            booking_required=False,
            source_data=attraction
        )
    
    @classmethod
    def from_event_data(cls, event: Dict[str, Any], ai_description: str = "") -> 'Activity':
        """Create Activity from event data."""
        # Convert rating to float if it's a string
        rating = event.get('rating')
        if rating is not None:
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                rating = None
        
        return cls(
            name=event.get('title', 'Unknown Event'),
            activity_type=ActivityType.EVENT,
            description=ai_description or event.get('description', 'A local event'),
            duration_hours=3.0,  # Default 3 hours for events
            cost_inr=event.get('price_inr', 500.0),  # Default ₹500
            location=event.get('venue', {}).get('name', ''),
            rating=rating,
            booking_required=True,
            source_data=event
        )
    
    @classmethod
    def from_flight_data(cls, flight: Dict[str, Any], flight_type: str = "outbound") -> 'Activity':
        """Create Activity from flight data."""
        flight_name = f"{flight_type.title()} Flight"
        if 'airline' in flight:
            flight_name = f"{flight['airline']} {flight_name}"
        
        # Extract flight details
        departure_time = flight.get('departure_time', 'TBD')
        arrival_time = flight.get('arrival_time', 'TBD')
        duration = flight.get('duration', 'Unknown')
        
        description = f"Flight from {flight.get('departure_airport', 'departure')} to {flight.get('arrival_airport', 'destination')}"
        if duration != 'Unknown':
            description += f" (Duration: {duration})"
        
        return cls(
            name=flight_name,
            activity_type=ActivityType.TRANSPORT,
            description=description,
            duration_hours=2.0,  # Default 2 hours for flight activity (including airport time)
            cost_inr=flight.get('price', 0.0),
            location=flight.get('departure_airport', ''),
            rating=None,
            start_time=departure_time,
            end_time=arrival_time,
            booking_required=True,
            source_data=flight
        )
    
    @classmethod
    def from_hotel_data(cls, hotel: Dict[str, Any]) -> 'Activity':
        """Create Activity from hotel data."""
        hotel_name = hotel.get('name', 'Hotel Accommodation')
        
        # Extract hotel details
        rating = hotel.get('rating', hotel.get('overall_rating'))
        if rating is not None:
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                rating = None
        
        # Get price per night
        price_info = hotel.get('rate_per_night', {})
        if isinstance(price_info, dict):
            cost = price_info.get('extracted_lowest', 0.0)
        else:
            cost = price_info or 0.0
        
        try:
            cost = float(cost) if cost else 0.0
        except (ValueError, TypeError):
            cost = 0.0
        
        description = f"Overnight stay at {hotel_name}"
        if hotel.get('neighborhood'):
            description += f" in {hotel['neighborhood']}"
        
        return cls(
            name=f"Stay at {hotel_name}",
            activity_type=ActivityType.ACCOMMODATION,
            description=description,
            duration_hours=12.0,  # 12 hours for overnight stay
            cost_inr=cost,
            location=hotel.get('address', hotel.get('neighborhood', '')),
            rating=rating,
            booking_required=True,
            source_data=hotel
        )


@dataclass
class DayPlan:
    """Plan for a single day of the trip."""
    day_number: int
    date: date
    activities: List[Activity]
    weather: WeatherInfo
    daily_cost_inr: float
    notes: str = ""
    
    def calculate_daily_cost(self) -> float:
        """Calculate total cost for this day."""
        return sum(activity.cost_inr for activity in self.activities)
    
    def get_activity_duration(self) -> float:
        """Get total planned activity duration in hours."""
        return sum(activity.duration_hours for activity in self.activities)


@dataclass
class Itinerary:
    """Complete itinerary for a trip."""
    trip_id: str
    days: List[DayPlan]
    total_cost_inr: float
    created_at: Optional[str] = None
    
    def calculate_total_cost(self) -> float:
        """Calculate total cost across all days."""
        return sum(day.daily_cost_inr for day in self.days)
    
    def get_total_duration(self) -> float:
        """Get total planned activity duration in hours."""
        return sum(day.get_activity_duration() for day in self.days)
    
    def get_activities_by_type(self, activity_type: ActivityType) -> List[Activity]:
        """Get all activities of a specific type across all days."""
        activities = []
        for day in self.days:
            activities.extend([activity for activity in day.activities if activity.activity_type == activity_type])
        return activities


@dataclass
class TripPlan:
    """Complete trip plan including preferences, itinerary, and costs."""
    id: str
    user_id: str
    preferences: 'TripPreferences'  # Forward reference
    itinerary: Itinerary
    cost_breakdown: 'CostBreakdown'  # Forward reference
    budget_status: 'BudgetStatus'  # Forward reference
    created_at: Optional[str] = None
    updated_at: Optional[str] = None