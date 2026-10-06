"""
Cost calculation service for the AI Trip Planner.

This service handles all cost calculations including flight costs, hotel costs,
attractions costs, events costs, and daily local expenses. It generates both
section-wise and day-wise cost breakdowns.
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from models.cost_models import CostBreakdown, DailyCost, BudgetStatus
from models.travel_data import TripData
from models.trip_preferences import TripPreferences, BudgetLevel
from services.currency_service import CurrencyService


class CostCalculationService:
    """Service for calculating trip costs and budget management."""
    
    def __init__(self):
        """Initialize the cost calculation service."""
        self.currency_service = CurrencyService()
        
        # Daily local expense estimates by budget level (in INR)
        self.daily_local_expenses = {
            BudgetLevel.LOW: 1500.0,      # ₹1,500 per day for budget travel
            BudgetLevel.MEDIUM: 3000.0,   # ₹3,000 per day for mid-range travel
            BudgetLevel.HIGH: 6000.0      # ₹6,000 per day for luxury travel
        }
    
    def calculate_trip_costs(
        self, 
        trip_data: TripData, 
        preferences: TripPreferences
    ) -> CostBreakdown:
        """
        Calculate complete trip costs with section-wise and day-wise breakdowns.
        
        Args:
            trip_data: Combined travel data from SERP API
            preferences: User trip preferences
            
        Returns:
            CostBreakdown: Complete cost breakdown with daily details
        """
        # Calculate section-wise costs
        flight_cost = self._calculate_flight_costs(trip_data.flights)
        hotel_cost = self._calculate_hotel_costs(trip_data.hotels, preferences.travel_days)
        attractions_cost = self._calculate_attractions_costs(trip_data.attractions)
        events_cost = self._calculate_events_costs(trip_data.events)
        local_expenses = self._calculate_local_expenses(preferences)
        
        # Calculate total cost
        total_cost = flight_cost + hotel_cost + attractions_cost + events_cost + local_expenses
        
        # Generate daily breakdown
        daily_breakdown = self._generate_daily_breakdown(
            preferences, flight_cost, hotel_cost, attractions_cost, 
            events_cost, local_expenses
        )
        
        return CostBreakdown(
            flight_cost_inr=flight_cost,
            hotel_cost_inr=hotel_cost,
            attractions_cost_inr=attractions_cost,
            events_cost_inr=events_cost,
            local_expenses_inr=local_expenses,
            total_cost_inr=total_cost,
            daily_breakdown=daily_breakdown
        )
    
    def _calculate_flight_costs(self, flight_data) -> float:
        """Calculate total flight costs in INR."""
        if not flight_data or not flight_data.flights:
            return 0.0
        
        total_cost = 0.0
        for flight in flight_data.flights[:2]:  # Consider top 2 flight options
            price_info = flight.get('price', 0)
            if isinstance(price_info, dict):
                price = price_info.get('value', 0)
                currency = price_info.get('currency', 'INR')
            else:
                price = price_info
                currency = 'INR'
            
            # Convert to INR if needed
            cost_inr = self.currency_service.convert_to_inr(price, currency)
            total_cost += cost_inr
        
        # Return average of considered flights
        return total_cost / min(len(flight_data.flights), 2) if flight_data.flights else 0.0
    
    def _calculate_hotel_costs(self, hotel_data, travel_days: int) -> float:
        """Calculate total hotel costs in INR."""
        if not hotel_data or not hotel_data.hotels:
            return 0.0
        
        # Get average price per night from available hotels
        total_per_night = 0.0
        hotel_count = 0
        
        for hotel in hotel_data.hotels[:5]:  # Consider top 5 hotels
            rate_info = hotel.get('rate_per_night', {})
            if isinstance(rate_info, dict):
                # Use extracted_lowest which should be a float
                price = rate_info.get('extracted_lowest', 0)
                # Check if the original price string contains INR symbol
                lowest_str = rate_info.get('lowest', '')
                if '₹' in str(lowest_str) or 'INR' in str(lowest_str).upper():
                    # Price is already in INR
                    cost_inr = float(price) if price else 0.0
                else:
                    # Convert from assumed USD
                    cost_inr = self.currency_service.convert_to_inr(price, 'USD')
            else:
                cost_inr = self.currency_service.convert_to_inr(rate_info, 'INR')
            
            if cost_inr > 0:
                total_per_night += cost_inr
                hotel_count += 1
        
        if hotel_count == 0:
            return 0.0
        
        avg_per_night = total_per_night / hotel_count
        # Calculate for nights needed (travel_days - 1, since you don't need hotel on last day)
        nights_needed = max(1, travel_days - 1)
        return avg_per_night * nights_needed
    
    def _calculate_attractions_costs(self, attraction_data) -> float:
        """Calculate total attractions costs in INR."""
        if not attraction_data or not attraction_data.attractions:
            return 0.0
        
        total_cost = 0.0
        for attraction in attraction_data.attractions:
            price = 0
            
            # Check if there's a price_inr field (added by our conversion)
            if 'price_inr' in attraction and attraction['price_inr']:
                price = attraction['price_inr']
            else:
                # Extract entry fee if available from other fields
                price_info = attraction.get('price')
                if isinstance(price_info, dict) and 'value' in price_info:
                    price = price_info.get('value', 0)
                elif price_info and price_info != 0:
                    price = price_info
                
                # If no price found or price is 0, use estimate
                if not price:
                    price = self._estimate_attraction_cost(attraction)
            
            # Convert to float and add to total
            try:
                price_float = float(price) if price else 0.0
                total_cost += price_float
            except (ValueError, TypeError):
                # If price is not a number, use estimate
                total_cost += self._estimate_attraction_cost(attraction)
        
        return total_cost
    
    def _calculate_events_costs(self, event_data) -> float:
        """Calculate total events costs in INR."""
        if not event_data or not event_data.events:
            return 0.0
        
        total_cost = 0.0
        for event in event_data.events:
            # Try to extract ticket price from various possible fields
            price = 0
            
            # Check ticket_info field (list or dict)
            ticket_info = event.get('ticket_info', [])
            if isinstance(ticket_info, list) and ticket_info:
                # ticket_info is a list, check first item
                first_ticket = ticket_info[0]
                if isinstance(first_ticket, dict):
                    price = first_ticket.get('price', 0)
            elif isinstance(ticket_info, dict):
                price = ticket_info.get('price', 0)
            
            # If no price found, check other possible fields
            if not price:
                price = event.get('price', 0)
            
            # If still no price, estimate based on event type
            if not price:
                price = self._estimate_event_cost(event)
            
            # Convert to float and add to total
            try:
                price_float = float(price) if price else 0.0
                total_cost += price_float
            except (ValueError, TypeError):
                # If price is not a number, use estimate
                total_cost += self._estimate_event_cost(event)
        
        return total_cost
    
    def _calculate_local_expenses(self, preferences: TripPreferences) -> float:
        """Calculate estimated daily local expenses in INR."""
        daily_expense = self.daily_local_expenses.get(
            preferences.budget_preference, 
            self.daily_local_expenses[BudgetLevel.MEDIUM]
        )
        return daily_expense * preferences.travel_days
    
    def _estimate_attraction_cost(self, attraction: Dict[str, Any]) -> float:
        """Estimate attraction cost based on type and rating."""
        # Default attraction costs in INR
        base_cost = 200.0  # ₹200 base entry fee
        
        # Adjust based on rating if available
        rating = attraction.get('rating', 3.0)
        try:
            rating = float(rating) if rating is not None else 3.0
        except (ValueError, TypeError):
            rating = 3.0
            
        if rating >= 4.5:
            base_cost *= 1.5  # Premium attractions
        elif rating >= 4.0:
            base_cost *= 1.2  # Popular attractions
        
        return base_cost
    
    def _estimate_event_cost(self, event: Dict[str, Any]) -> float:
        """Estimate event cost based on type and venue."""
        # Default event costs in INR
        base_cost = 500.0  # ₹500 base ticket price
        
        # Adjust based on event type
        event_title = event.get('title', '').lower()
        if any(keyword in event_title for keyword in ['concert', 'festival', 'show']):
            base_cost *= 2.0  # Entertainment events
        elif any(keyword in event_title for keyword in ['museum', 'gallery', 'exhibition']):
            base_cost *= 0.6  # Cultural events
        
        return base_cost
    
    def _generate_daily_breakdown(
        self, 
        preferences: TripPreferences,
        flight_cost: float,
        hotel_cost: float,
        attractions_cost: float,
        events_cost: float,
        local_expenses: float
    ) -> List[DailyCost]:
        """Generate day-wise cost breakdown."""
        daily_breakdown = []
        
        # Calculate daily averages
        daily_hotel = hotel_cost / preferences.travel_days
        daily_attractions = attractions_cost / preferences.travel_days
        daily_events = events_cost / preferences.travel_days
        daily_local = local_expenses / preferences.travel_days
        
        # Distribute flight costs (arrival day and departure day)
        if preferences.travel_days == 1:
            # For single day trips, put all flight cost on that day
            flight_arrival = flight_cost
            flight_departure = 0.0
        else:
            flight_arrival = flight_cost * 0.6  # 60% on arrival
            flight_departure = flight_cost * 0.4  # 40% on departure
        
        current_date = preferences.start_date
        for day in range(preferences.travel_days):
            # Flight costs distribution
            day_flight_cost = 0.0
            if day == 0:  # First day
                day_flight_cost = flight_arrival
            elif day == preferences.travel_days - 1:  # Last day
                day_flight_cost = flight_departure
            
            daily_total = (day_flight_cost + daily_hotel + daily_attractions + 
                          daily_events + daily_local)
            
            daily_cost = DailyCost(
                day_number=day + 1,
                date=current_date,
                flight_cost_inr=day_flight_cost,
                hotel_cost_inr=daily_hotel,
                attractions_cost_inr=daily_attractions,
                events_cost_inr=daily_events,
                local_expenses_inr=daily_local,
                total_cost_inr=daily_total
            )
            
            daily_breakdown.append(daily_cost)
            current_date += timedelta(days=1)
        
        return daily_breakdown
    
    def calculate_budget_status(
        self, 
        cost_breakdown: CostBreakdown, 
        max_budget_inr: float
    ) -> BudgetStatus:
        """Calculate budget status and generate suggestions."""
        return BudgetStatus.calculate_status(
            cost_breakdown.total_cost_inr, 
            max_budget_inr
        )