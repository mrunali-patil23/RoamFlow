"""
Trip preferences router for FastAPI.
Handles trip preference validation and processing.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import date, datetime
from models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
from routers.auth import get_current_user_dependency
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trip-preferences", tags=["trip-preferences"])

# Request/Response Models
class TripPreferencesRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    travel_days: int
    travel_type: str
    budget_preference: str
    max_budget_inr: float
    interests: List[str]
    
    @field_validator('destination')
    @classmethod
    def validate_destination(cls, v):
        if not v or not v.strip():
            raise ValueError('Destination cannot be empty')
        return v.strip()
    
    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v):
        if v < date.today():
            raise ValueError('Start date must be in the future')
        return v
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @field_validator('travel_days')
    @classmethod
    def validate_travel_days(cls, v):
        if v <= 0:
            raise ValueError('Travel days must be positive')
        if v > 365:
            raise ValueError('Travel days cannot exceed 365')
        return v
    
    @field_validator('travel_type')
    @classmethod
    def validate_travel_type(cls, v):
        try:
            TravelType(v)
        except ValueError:
            valid_types = [t.value for t in TravelType]
            raise ValueError(f'Travel type must be one of: {valid_types}')
        return v
    
    @field_validator('budget_preference')
    @classmethod
    def validate_budget_preference(cls, v):
        try:
            BudgetLevel(v)
        except ValueError:
            valid_levels = [b.value for b in BudgetLevel]
            raise ValueError(f'Budget preference must be one of: {valid_levels}')
        return v
    
    @field_validator('max_budget_inr')
    @classmethod
    def validate_max_budget(cls, v):
        if v <= 0:
            raise ValueError('Maximum budget must be positive')
        if v > 10000000:  # 1 crore INR limit
            raise ValueError('Maximum budget cannot exceed ₹1,00,00,000')
        return v
    
    @field_validator('interests')
    @classmethod
    def validate_interests(cls, v):
        if not v:
            raise ValueError('At least one interest must be selected')
        
        valid_interests = [i.value for i in Interest]
        for interest in v:
            if interest not in valid_interests:
                raise ValueError(f'Interest "{interest}" is not valid. Valid interests: {valid_interests}')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_interests = []
        for interest in v:
            if interest not in seen:
                seen.add(interest)
                unique_interests.append(interest)
        
        return unique_interests

class ValidationResponse(BaseModel):
    valid: bool
    message: str
    errors: Optional[List[str]] = None

class TripPreferencesResponse(BaseModel):
    destination: str
    start_date: date
    end_date: date
    travel_days: int
    travel_type: str
    budget_preference: str
    max_budget_inr: float
    interests: List[str]
    validation_status: str

# Trip preferences validation endpoints
@router.post("/validate", response_model=ValidationResponse)
async def validate_trip_preferences(
    request: TripPreferencesRequest,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Validate trip preferences data.
    Performs comprehensive validation of all trip preference fields.
    """
    try:
        # Convert request to TripPreferences model for additional validation
        travel_type = TravelType(request.travel_type)
        budget_level = BudgetLevel(request.budget_preference)
        interests = [Interest(i) for i in request.interests]
        
        trip_prefs = TripPreferences(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            travel_days=request.travel_days,
            travel_type=travel_type,
            budget_preference=budget_level,
            max_budget_inr=request.max_budget_inr,
            interests=interests
        )
        
        return ValidationResponse(
            valid=True,
            message="Trip preferences are valid"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error for user {current_user['id']}: {e}")
        return ValidationResponse(
            valid=False,
            message="Validation failed",
            errors=[str(e)]
        )
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation service temporarily unavailable"
        )

@router.post("/validate-dates", response_model=ValidationResponse)
async def validate_dates(
    start_date: date,
    end_date: date,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Validate trip dates specifically.
    Checks that dates are in the future and end date is after start date.
    """
    try:
        errors = []
        
        # Validate start date is in the future
        if start_date < date.today():
            errors.append("Start date must be in the future")
        
        # Validate end date is after start date
        if end_date <= start_date:
            errors.append("End date must be after start date")
        
        # Check for reasonable date range (not more than 2 years in advance)
        max_advance_date = date.today().replace(year=date.today().year + 2)
        if start_date > max_advance_date:
            errors.append("Start date cannot be more than 2 years in advance")
        
        if errors:
            return ValidationResponse(
                valid=False,
                message="Date validation failed",
                errors=errors
            )
        
        return ValidationResponse(
            valid=True,
            message="Dates are valid"
        )
        
    except Exception as e:
        logger.error(f"Date validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Date validation service temporarily unavailable"
        )

@router.post("/validate-budget", response_model=ValidationResponse)
async def validate_budget(
    max_budget_inr: float,
    travel_days: int,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Validate budget and travel days.
    Checks budget is positive and reasonable for the number of travel days.
    """
    try:
        errors = []
        
        # Validate budget is positive
        if max_budget_inr <= 0:
            errors.append("Maximum budget must be positive")
        
        # Validate budget is not unreasonably high
        if max_budget_inr > 10000000:  # 1 crore INR
            errors.append("Maximum budget cannot exceed ₹1,00,00,000")
        
        # Validate travel days
        if travel_days <= 0:
            errors.append("Travel days must be positive")
        
        if travel_days > 365:
            errors.append("Travel days cannot exceed 365")
        
        # Validate budget reasonableness for travel days
        if max_budget_inr > 0 and travel_days > 0:
            daily_budget = max_budget_inr / travel_days
            if daily_budget < 1000:  # Less than ₹1000 per day
                errors.append("Budget may be too low for the number of travel days (minimum ₹1000 per day recommended)")
        
        if errors:
            return ValidationResponse(
                valid=False,
                message="Budget validation failed",
                errors=errors
            )
        
        return ValidationResponse(
            valid=True,
            message="Budget and travel days are valid"
        )
        
    except Exception as e:
        logger.error(f"Budget validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Budget validation service temporarily unavailable"
        )

@router.get("/options")
async def get_preference_options():
    """
    Get available options for trip preferences.
    Returns valid values for travel types, budget levels, and interests.
    """
    try:
        return {
            "travel_types": [t.value for t in TravelType],
            "budget_levels": [b.value for b in BudgetLevel],
            "interests": [i.value for i in Interest]
        }
    except Exception as e:
        logger.error(f"Error getting preference options: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve preference options"
        )