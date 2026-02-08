"""
API-specific Pydantic models for the AI Travel Planner.

This module defines models for API requests, responses, and error handling.
"""

from typing import Any, Dict, List, Optional
from datetime import date
from pydantic import BaseModel, Field
from .trip_models import TripItinerary, BudgetCategory, TravelerType


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"key": "value"},
                "message": "Request completed successfully"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for error responses")
    error: bool = Field(True, description="Always true for error responses")
    message: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code for programmatic handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "success": False,
                "error": True,
                "message": "Validation error occurred",
                "error_code": "VALIDATION_ERROR",
                "details": {"field": "destination", "issue": "cannot be empty"},
                "retry_after": None
            }
        }


class TripRequest(BaseModel):
    """Request model for trip planning."""
    destination: str = Field(..., min_length=1, description="Travel destination")
    days: int = Field(..., ge=1, le=30, description="Number of days for the trip")
    budget: BudgetCategory = Field(..., description="Budget category preference")
    travelers: TravelerType = Field(..., description="Type of travelers")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "destination": "Paris, France",
                "days": 5,
                "budget": "moderate",
                "travelers": "couple"
            }
        }


class TripResponse(BaseModel):
    """Response model for trip planning results."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[TripItinerary] = Field(None, description="Generated trip itinerary")
    message: str = Field(..., description="Response message")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "trip_id": "trip_123",
                    "destination": "Paris, France",
                    "total_days": 5,
                    "daily_plans": [],
                    "total_budget": 1500.0
                },
                "message": "Trip itinerary generated successfully"
            }
        }


class TransportResponse(BaseModel):
    """Response model for transport-related requests."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Transport data")
    message: str = Field(..., description="Response message")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"flights": [], "local_transport": []},
                "message": "Transport options retrieved successfully"
            }
        }


class FlightSearchParams(BaseModel):
    """Parameters for flight search requests."""
    origin: str = Field(..., min_length=1, description="Origin airport code or city")
    destination: str = Field(..., min_length=1, description="Destination airport code or city")
    departure_date: date = Field(..., description="Departure date")
    return_date: Optional[date] = Field(None, description="Return date for round trip")
    passengers: int = Field(1, ge=1, le=9, description="Number of passengers")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "origin": "JFK",
                "destination": "CDG",
                "departure_date": "2024-06-15",
                "return_date": "2024-06-22",
                "passengers": 2
            }
        }


class FlightOption(BaseModel):
    """Model for individual flight options."""
    airline: str = Field(..., description="Airline name")
    flight_number: str = Field(..., description="Flight number")
    departure_time: str = Field(..., description="Departure time")
    arrival_time: str = Field(..., description="Arrival time")
    duration: int = Field(..., ge=30, description="Flight duration in minutes")
    price: float = Field(..., ge=0, description="Price in USD")
    stops: int = Field(0, ge=0, description="Number of stops")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "airline": "Air France",
                "flight_number": "AF83",
                "departure_time": "14:30",
                "arrival_time": "16:45",
                "duration": 495,
                "price": 650.00,
                "stops": 0
            }
        }


class FlightOptions(BaseModel):
    """Response model for flight search results."""
    flights: List[FlightOption] = Field(..., description="List of available flights")
    search_params: FlightSearchParams = Field(..., description="Original search parameters")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "flights": [
                    {
                        "airline": "Air France",
                        "flight_number": "AF83",
                        "departure_time": "14:30",
                        "arrival_time": "16:45",
                        "duration": 495,
                        "price": 650.00,
                        "stops": 0
                    }
                ],
                "search_params": {
                    "origin": "JFK",
                    "destination": "CDG",
                    "departure_date": "2024-06-15",
                    "return_date": "2024-06-22",
                    "passengers": 2
                }
            }
        }


class TransportRequest(BaseModel):
    """Request model for local transport options."""
    location: str = Field(..., min_length=1, description="Location for transport search")
    transport_type: Optional[str] = Field(None, description="Specific transport type filter")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "location": "Paris, France",
                "transport_type": "metro"
            }
        }


class TransportOptions(BaseModel):
    """Response model for local transport options."""
    location: str = Field(..., description="Location for the transport options")
    options: List[Dict[str, Any]] = Field(..., description="Available transport options")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "location": "Paris, France",
                "options": [
                    {
                        "type": "metro",
                        "provider": "RATP",
                        "cost_per_ride": 1.90,
                        "day_pass": 7.50
                    },
                    {
                        "type": "taxi",
                        "provider": "G7",
                        "base_fare": 2.60,
                        "per_km": 1.06
                    }
                ]
            }
        }