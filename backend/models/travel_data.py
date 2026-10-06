"""
Travel data models for SERP API responses.

This module defines data structures for flight, hotel, attraction, event, and weather data
returned from SERP API integration.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Dict, Any


@dataclass
class DateRange:
    """Date range for travel queries."""
    start_date: date
    end_date: date


@dataclass
class FlightData:
    """Flight information from SERP API."""
    flights: List[Dict[str, Any]]
    total_results: int
    search_metadata: Dict[str, Any]
    
    @classmethod
    def from_serp_response(cls, response: Dict[str, Any]) -> 'FlightData':
        """Create FlightData from SERP API response."""
        return cls(
            flights=response.get('best_flights', []) + response.get('other_flights', []),
            total_results=len(response.get('best_flights', []) + response.get('other_flights', [])),
            search_metadata=response.get('search_metadata', {})
        )


@dataclass
class HotelData:
    """Hotel information from SERP API."""
    hotels: List[Dict[str, Any]]
    total_results: int
    search_metadata: Dict[str, Any]
    
    @classmethod
    def from_serp_response(cls, response: Dict[str, Any]) -> 'HotelData':
        """Create HotelData from SERP API response."""
        return cls(
            hotels=response.get('properties', []),
            total_results=len(response.get('properties', [])),
            search_metadata=response.get('search_metadata', {})
        )


@dataclass
class AttractionData:
    """Attraction information from SERP API."""
    attractions: List[Dict[str, Any]]
    total_results: int
    search_metadata: Dict[str, Any]
    
    @classmethod
    def from_serp_response(cls, response: Dict[str, Any]) -> 'AttractionData':
        """Create AttractionData from SERP API response."""
        return cls(
            attractions=response.get('local_results', []),
            total_results=len(response.get('local_results', [])),
            search_metadata=response.get('search_metadata', {})
        )


@dataclass
class EventData:
    """Event information from SERP API."""
    events: List[Dict[str, Any]]
    total_results: int
    search_metadata: Dict[str, Any]
    
    @classmethod
    def from_serp_response(cls, response: Dict[str, Any]) -> 'EventData':
        """Create EventData from SERP API response."""
        return cls(
            events=response.get('events_results', []),
            total_results=len(response.get('events_results', [])),
            search_metadata=response.get('search_metadata', {})
        )


@dataclass
class WeatherData:
    """Weather information from SERP API."""
    current_weather: Dict[str, Any]
    forecast: List[Dict[str, Any]]
    location: str
    search_metadata: Dict[str, Any]
    
    @classmethod
    def from_serp_response(cls, response: Dict[str, Any]) -> 'WeatherData':
        """Create WeatherData from SERP API response."""
        return cls(
            current_weather=response.get('current', {}),
            forecast=response.get('forecast', []),
            location=response.get('location', ''),
            search_metadata=response.get('search_metadata', {})
        )


@dataclass
class TripData:
    """Combined trip data from all SERP API sources."""
    flights: Optional[FlightData] = None
    hotels: Optional[HotelData] = None
    attractions: Optional[AttractionData] = None
    events: Optional[EventData] = None
    weather: Optional[WeatherData] = None