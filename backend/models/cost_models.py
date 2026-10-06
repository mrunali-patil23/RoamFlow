"""
Cost calculation models for the AI Trip Planner.

This module defines data structures for cost calculations, budget management,
and cost breakdowns as specified in the design document.
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class DailyCost:
    """Daily cost breakdown for a specific day."""
    day_number: int
    date: date
    flight_cost_inr: float
    hotel_cost_inr: float
    attractions_cost_inr: float
    events_cost_inr: float
    local_expenses_inr: float
    total_cost_inr: float


@dataclass
class CostBreakdown:
    """Complete cost breakdown for a trip."""
    flight_cost_inr: float
    hotel_cost_inr: float
    attractions_cost_inr: float
    events_cost_inr: float
    local_expenses_inr: float
    total_cost_inr: float
    daily_breakdown: List[DailyCost]


@dataclass
class BudgetStatus:
    """Budget status classification and suggestions."""
    status: str  # "Within Budget", "Slightly Over Budget", "Over Budget"
    difference_inr: float
    suggestions: List[str]
    
    @classmethod
    def calculate_status(cls, total_cost_inr: float, max_budget_inr: float) -> 'BudgetStatus':
        """Calculate budget status based on total cost and maximum budget."""
        difference = total_cost_inr - max_budget_inr
        
        if difference <= 0:
            status = "Within Budget"
            suggestions = []
        elif difference <= (max_budget_inr * 0.1):  # Within 10% over budget
            status = "Slightly Over Budget"
            suggestions = [
                "Consider choosing a lower-rated hotel to reduce accommodation costs",
                "Look for free or low-cost attractions and activities",
                "Reduce daily local expenses by eating at local restaurants"
            ]
        else:
            status = "Over Budget"
            suggestions = [
                "Choose budget airlines or flights with layovers to reduce flight costs",
                "Select budget accommodations or hostels instead of hotels",
                "Focus on free attractions like parks, museums with free entry days",
                "Reduce the number of paid activities and events",
                "Consider shortening the trip duration to reduce overall costs"
            ]
        
        return cls(
            status=status,
            difference_inr=difference,
            suggestions=suggestions
        )