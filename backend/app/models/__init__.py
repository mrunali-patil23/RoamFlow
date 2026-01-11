# Data models package

from .trip_models import (
    BudgetCategory,
    TravelerType,
    ActivityCategory,
    TransportType,
    TripRequest,
    Activity,
    TransportOption,
    DayPlan,
    TripItinerary,
)

from .api_models import (
    APIResponse,
    ErrorResponse,
    FlightSearchParams,
    FlightOption,
    FlightOptions,
    TransportRequest,
    TransportOptions,
)

__all__ = [
    # Trip models
    "BudgetCategory",
    "TravelerType", 
    "ActivityCategory",
    "TransportType",
    "TripRequest",
    "Activity",
    "TransportOption",
    "DayPlan",
    "TripItinerary",
    # API models
    "APIResponse",
    "ErrorResponse",
    "FlightSearchParams",
    "FlightOption",
    "FlightOptions",
    "TransportRequest",
    "TransportOptions",
]