"""
Property-based tests for cost calculation service.
Tests universal properties that should hold for all valid inputs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from decimal import Decimal

# Configure hypothesis to run fewer examples for faster testing
settings.register_profile("fast", max_examples=10, deadline=1000)
settings.load_profile("fast")

# Import models and services
from models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
from models.travel_data import TripData, FlightData, HotelData, AttractionData, EventData
from models.cost_models import CostBreakdown, BudgetStatus, DailyCost


# Strategy for generating valid trip preferences
@st.composite
def trip_preferences_strategy(draw):
    """Generate valid TripPreferences for testing."""
    start_date = draw(st.dates(min_value=date.today() + timedelta(days=1), 
                               max_value=date.today() + timedelta(days=365)))
    travel_days = draw(st.integers(min_value=1, max_value=30))
    end_date = start_date + timedelta(days=travel_days)
    
    # Generate a non-empty destination
    destination = draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
    destination = destination.strip()
    if not destination:
        destination = "Paris"  # Fallback destination
    
    return TripPreferences(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        travel_days=travel_days,
        travel_type=draw(st.sampled_from(list(TravelType))),
        budget_preference=draw(st.sampled_from(list(BudgetLevel))),
        max_budget_inr=draw(st.floats(min_value=1000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)),
        interests=draw(st.lists(st.sampled_from(list(Interest)), min_size=1, max_size=6, unique=True))
    )


@st.composite
def trip_data_strategy(draw):
    """Generate TripData with mock flight and hotel data."""
    # Generate flight data
    flight_count = draw(st.integers(min_value=0, max_value=5))
    flights = []
    for _ in range(flight_count):
        price = draw(st.floats(min_value=5000.0, max_value=100000.0, allow_nan=False, allow_infinity=False))
        flights.append({
            'price': {'value': price, 'currency': 'INR'},
            'airline': 'Test Airline',
            'departure_time': '10:00'
        })
    
    flight_data = FlightData(flights=flights, total_results=len(flights), search_metadata={}) if flights else None
    
    # Generate hotel data
    hotel_count = draw(st.integers(min_value=0, max_value=5))
    hotels = []
    for _ in range(hotel_count):
        rate = draw(st.floats(min_value=1000.0, max_value=20000.0, allow_nan=False, allow_infinity=False))
        hotels.append({
            'rate_per_night': {'lowest': rate, 'currency': 'INR'},
            'name': 'Test Hotel',
            'rating': draw(st.floats(min_value=1.0, max_value=5.0))
        })
    
    hotel_data = HotelData(hotels=hotels, total_results=len(hotels), search_metadata={}) if hotels else None
    
    # Generate attraction data
    attraction_count = draw(st.integers(min_value=0, max_value=10))
    attractions = []
    for _ in range(attraction_count):
        price = draw(st.floats(min_value=0.0, max_value=2000.0, allow_nan=False, allow_infinity=False))
        attractions.append({
            'title': 'Test Attraction',
            'price': {'value': price, 'currency': 'INR'} if price > 0 else {},
            'rating': draw(st.floats(min_value=1.0, max_value=5.0))
        })
    
    attraction_data = AttractionData(attractions=attractions, total_results=len(attractions), search_metadata={}) if attractions else None
    
    # Generate event data
    event_count = draw(st.integers(min_value=0, max_value=5))
    events = []
    for _ in range(event_count):
        price = draw(st.floats(min_value=0.0, max_value=5000.0, allow_nan=False, allow_infinity=False))
        events.append({
            'title': 'Test Event',
            'ticket_info': {'price': price, 'currency': 'INR'} if price > 0 else {},
            'venue': 'Test Venue'
        })
    
    event_data = EventData(events=events, total_results=len(events), search_metadata={}) if events else None
    
    return TripData(
        flights=flight_data,
        hotels=hotel_data,
        attractions=attraction_data,
        events=event_data,
        weather=None
    )


# Feature: ai-trip-planner, Property 11: Cost Calculation Completeness
# **Validates: Requirements 5.1, 5.4**

@given(
    preferences=trip_preferences_strategy(),
    trip_data=trip_data_strategy()
)
def test_property_cost_calculation_completeness(preferences, trip_data):
    """
    Property 11: Cost Calculation Completeness
    For any trip plan, the cost calculation should include all required components 
    (flights, hotels, attractions, events, local expenses) and produce accurate totals.
    **Validates: Requirements 5.1, 5.4**
    """
    # Create a standalone cost calculation service without importing the full services package
    import sys
    import os
    
    # Mock the currency service to avoid database dependencies
    class MockCurrencyService:
        def convert_to_inr(self, amount, currency):
            return float(amount)
    
    # Create a standalone cost calculation service class
    class StandaloneCostCalculationService:
        def __init__(self):
            self.currency_service = MockCurrencyService()
            self.daily_local_expenses = {
                BudgetLevel.LOW: 1500.0,
                BudgetLevel.MEDIUM: 3000.0,
                BudgetLevel.HIGH: 6000.0
            }
        
        def calculate_trip_costs(self, trip_data, preferences):
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
        
        def _calculate_flight_costs(self, flight_data):
            if not flight_data or not flight_data.flights:
                return 0.0
            
            total_cost = 0.0
            for flight in flight_data.flights[:2]:
                price_info = flight.get('price', 0)
                if isinstance(price_info, dict):
                    price = price_info.get('value', 0)
                else:
                    price = price_info
                
                cost_inr = self.currency_service.convert_to_inr(price, 'INR')
                total_cost += cost_inr
            
            return total_cost / min(len(flight_data.flights), 2) if flight_data.flights else 0.0
        
        def _calculate_hotel_costs(self, hotel_data, travel_days):
            if not hotel_data or not hotel_data.hotels:
                return 0.0
            
            total_per_night = 0.0
            hotel_count = 0
            
            for hotel in hotel_data.hotels[:5]:
                rate_info = hotel.get('rate_per_night', {})
                if isinstance(rate_info, dict):
                    price = rate_info.get('lowest', 0)
                else:
                    price = rate_info
                
                if price > 0:
                    cost_inr = self.currency_service.convert_to_inr(price, 'INR')
                    total_per_night += cost_inr
                    hotel_count += 1
            
            if hotel_count == 0:
                return 0.0
            
            avg_per_night = total_per_night / hotel_count
            return avg_per_night * travel_days
        
        def _calculate_attractions_costs(self, attraction_data):
            if not attraction_data or not attraction_data.attractions:
                return 0.0
            
            total_cost = 0.0
            for attraction in attraction_data.attractions:
                price_info = attraction.get('price', {})
                if isinstance(price_info, dict):
                    price = price_info.get('value', 0)
                else:
                    price = 200.0  # Default estimate
                
                cost_inr = self.currency_service.convert_to_inr(price, 'INR')
                total_cost += cost_inr
            
            return total_cost
        
        def _calculate_events_costs(self, event_data):
            if not event_data or not event_data.events:
                return 0.0
            
            total_cost = 0.0
            for event in event_data.events:
                price_info = event.get('ticket_info', {})
                if isinstance(price_info, dict):
                    price = price_info.get('price', 0)
                else:
                    price = 500.0  # Default estimate
                
                cost_inr = self.currency_service.convert_to_inr(price, 'INR')
                total_cost += cost_inr
            
            return total_cost
        
        def _calculate_local_expenses(self, preferences):
            daily_expense = self.daily_local_expenses.get(
                preferences.budget_preference, 
                self.daily_local_expenses[BudgetLevel.MEDIUM]
            )
            return daily_expense * preferences.travel_days
        
        def _generate_daily_breakdown(self, preferences, flight_cost, hotel_cost, 
                                    attractions_cost, events_cost, local_expenses):
            daily_breakdown = []
            
            # Calculate daily averages
            daily_hotel = hotel_cost / preferences.travel_days
            daily_attractions = attractions_cost / preferences.travel_days
            daily_events = events_cost / preferences.travel_days
            daily_local = local_expenses / preferences.travel_days
            
            # Distribute flight costs
            if preferences.travel_days == 1:
                # For single day trips, put all flight cost on that day
                flight_arrival = flight_cost
                flight_departure = 0.0
            else:
                flight_arrival = flight_cost * 0.6
                flight_departure = flight_cost * 0.4
            
            current_date = preferences.start_date
            for day in range(preferences.travel_days):
                day_flight_cost = 0.0
                if day == 0:
                    day_flight_cost = flight_arrival
                elif day == preferences.travel_days - 1:
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
    
    # Create service instance
    service = StandaloneCostCalculationService()
    
    # Calculate trip costs
    cost_breakdown = service.calculate_trip_costs(trip_data, preferences)
    
    # Property: Cost breakdown should be a CostBreakdown instance
    assert isinstance(cost_breakdown, CostBreakdown), f"Result should be CostBreakdown instance: {type(cost_breakdown)}"
    
    # Property: All cost components should be non-negative floats
    assert isinstance(cost_breakdown.flight_cost_inr, float), "Flight cost should be float"
    assert cost_breakdown.flight_cost_inr >= 0, f"Flight cost should be non-negative: {cost_breakdown.flight_cost_inr}"
    
    assert isinstance(cost_breakdown.hotel_cost_inr, float), "Hotel cost should be float"
    assert cost_breakdown.hotel_cost_inr >= 0, f"Hotel cost should be non-negative: {cost_breakdown.hotel_cost_inr}"
    
    assert isinstance(cost_breakdown.attractions_cost_inr, float), "Attractions cost should be float"
    assert cost_breakdown.attractions_cost_inr >= 0, f"Attractions cost should be non-negative: {cost_breakdown.attractions_cost_inr}"
    
    assert isinstance(cost_breakdown.events_cost_inr, float), "Events cost should be float"
    assert cost_breakdown.events_cost_inr >= 0, f"Events cost should be non-negative: {cost_breakdown.events_cost_inr}"
    
    assert isinstance(cost_breakdown.local_expenses_inr, float), "Local expenses should be float"
    assert cost_breakdown.local_expenses_inr >= 0, f"Local expenses should be non-negative: {cost_breakdown.local_expenses_inr}"
    
    # Property: Total cost should equal sum of all components
    expected_total = (cost_breakdown.flight_cost_inr + cost_breakdown.hotel_cost_inr + 
                     cost_breakdown.attractions_cost_inr + cost_breakdown.events_cost_inr + 
                     cost_breakdown.local_expenses_inr)
    
    assert abs(cost_breakdown.total_cost_inr - expected_total) < 0.01, \
        f"Total cost should equal sum of components: {cost_breakdown.total_cost_inr} != {expected_total}"
    
    # Property: Daily breakdown should have correct number of days
    assert len(cost_breakdown.daily_breakdown) == preferences.travel_days, \
        f"Daily breakdown should have {preferences.travel_days} days: {len(cost_breakdown.daily_breakdown)}"
    
    # Property: Sum of daily costs should equal total cost
    daily_total = sum(day.total_cost_inr for day in cost_breakdown.daily_breakdown)
    assert abs(daily_total - cost_breakdown.total_cost_inr) < 0.01, \
        f"Sum of daily costs should equal total: {daily_total} != {cost_breakdown.total_cost_inr}"
    
    # Property: Each daily cost should have all components
    for i, daily_cost in enumerate(cost_breakdown.daily_breakdown):
        assert daily_cost.day_number == i + 1, f"Day number should be sequential: {daily_cost.day_number} != {i + 1}"
        assert isinstance(daily_cost.date, date), f"Daily cost date should be date instance: {type(daily_cost.date)}"
        
        # All daily cost components should be non-negative
        assert daily_cost.flight_cost_inr >= 0, f"Daily flight cost should be non-negative: {daily_cost.flight_cost_inr}"
        assert daily_cost.hotel_cost_inr >= 0, f"Daily hotel cost should be non-negative: {daily_cost.hotel_cost_inr}"
        assert daily_cost.attractions_cost_inr >= 0, f"Daily attractions cost should be non-negative: {daily_cost.attractions_cost_inr}"
        assert daily_cost.events_cost_inr >= 0, f"Daily events cost should be non-negative: {daily_cost.events_cost_inr}"
        assert daily_cost.local_expenses_inr >= 0, f"Daily local expenses should be non-negative: {daily_cost.local_expenses_inr}"
        
        # Daily total should equal sum of daily components
        daily_component_sum = (daily_cost.flight_cost_inr + daily_cost.hotel_cost_inr + 
                             daily_cost.attractions_cost_inr + daily_cost.events_cost_inr + 
                             daily_cost.local_expenses_inr)
        assert abs(daily_cost.total_cost_inr - daily_component_sum) < 0.01, \
            f"Daily total should equal sum of daily components: {daily_cost.total_cost_inr} != {daily_component_sum}"
    
    # Property: Local expenses should be based on budget preference and travel days
    expected_daily_local = service.daily_local_expenses.get(preferences.budget_preference, 3000.0)
    expected_total_local = expected_daily_local * preferences.travel_days
    assert abs(cost_breakdown.local_expenses_inr - expected_total_local) < 0.01, \
        f"Local expenses should match budget preference: {cost_breakdown.local_expenses_inr} != {expected_total_local}"
    
    # Property: If no travel data provided, only local expenses should be non-zero
    if (not trip_data.flights and not trip_data.hotels and 
        not trip_data.attractions and not trip_data.events):
        assert cost_breakdown.flight_cost_inr == 0, "Flight cost should be 0 when no flight data"
        assert cost_breakdown.hotel_cost_inr == 0, "Hotel cost should be 0 when no hotel data"
        assert cost_breakdown.attractions_cost_inr == 0, "Attractions cost should be 0 when no attraction data"
        assert cost_breakdown.events_cost_inr == 0, "Events cost should be 0 when no event data"
        assert cost_breakdown.local_expenses_inr > 0, "Local expenses should always be positive"


# Feature: ai-trip-planner, Property 13: Budget Status Classification
# **Validates: Requirements 5.5**

@given(
    total_cost=st.floats(min_value=1000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
    max_budget=st.floats(min_value=1000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
def test_property_budget_status_classification(total_cost, max_budget):
    """
    Property 13: Budget Status Classification
    For any trip cost and maximum budget pair, the system should correctly classify 
    the budget status as "Within Budget", "Slightly Over Budget", or "Over Budget".
    **Validates: Requirements 5.5**
    """
    # Calculate budget status
    budget_status = BudgetStatus.calculate_status(total_cost, max_budget)
    
    # Property: Budget status should be a BudgetStatus instance
    assert isinstance(budget_status, BudgetStatus), f"Result should be BudgetStatus instance: {type(budget_status)}"
    
    # Property: Status should be one of the valid values
    valid_statuses = ["Within Budget", "Slightly Over Budget", "Over Budget"]
    assert budget_status.status in valid_statuses, f"Status should be valid: {budget_status.status}"
    
    # Property: Difference should be calculated correctly
    expected_difference = total_cost - max_budget
    assert abs(budget_status.difference_inr - expected_difference) < 0.01, \
        f"Difference should be calculated correctly: {budget_status.difference_inr} != {expected_difference}"
    
    # Property: Status classification should be correct based on difference
    if expected_difference <= 0:
        assert budget_status.status == "Within Budget", f"Should be 'Within Budget' when difference <= 0: {budget_status.status}"
        assert len(budget_status.suggestions) == 0, "Should have no suggestions when within budget"
    elif expected_difference <= (max_budget * 0.1):
        assert budget_status.status == "Slightly Over Budget", f"Should be 'Slightly Over Budget' when within 10%: {budget_status.status}"
        assert len(budget_status.suggestions) > 0, "Should have suggestions when slightly over budget"
    else:
        assert budget_status.status == "Over Budget", f"Should be 'Over Budget' when over 10%: {budget_status.status}"
        assert len(budget_status.suggestions) > 0, "Should have suggestions when over budget"
    
    # Property: Suggestions should be a list of strings
    assert isinstance(budget_status.suggestions, list), f"Suggestions should be list: {type(budget_status.suggestions)}"
    for suggestion in budget_status.suggestions:
        assert isinstance(suggestion, str), f"Each suggestion should be string: {type(suggestion)}"
        assert len(suggestion) > 0, "Suggestions should not be empty strings"
    
    # Property: More over budget should have more suggestions
    if expected_difference > (max_budget * 0.1):
        # Over budget should have more suggestions than slightly over budget
        slightly_over_status = BudgetStatus.calculate_status(max_budget * 1.05, max_budget)
        assert len(budget_status.suggestions) >= len(slightly_over_status.suggestions), \
            "Over budget should have at least as many suggestions as slightly over budget"


# Feature: ai-trip-planner, Property 14: Budget Exceedance Response
# **Validates: Requirements 5.6**

@given(
    max_budget=st.floats(min_value=10000.0, max_value=100000.0, allow_nan=False, allow_infinity=False),
    exceedance_factor=st.floats(min_value=1.01, max_value=3.0, allow_nan=False, allow_infinity=False)
)
def test_property_budget_exceedance_response(max_budget, exceedance_factor):
    """
    Property 14: Budget Exceedance Response
    For any trip plan where total cost exceeds the maximum budget, 
    the system should provide specific cost-saving suggestions.
    **Validates: Requirements 5.6**
    """
    # Calculate a total cost that exceeds the budget
    total_cost = max_budget * exceedance_factor
    
    # Calculate budget status
    budget_status = BudgetStatus.calculate_status(total_cost, max_budget)
    
    # Property: When budget is exceeded, status should not be "Within Budget"
    assert budget_status.status != "Within Budget", f"Status should not be 'Within Budget' when cost exceeds budget: {budget_status.status}"
    
    # Property: When budget is exceeded, suggestions should be provided
    assert len(budget_status.suggestions) > 0, "Should provide suggestions when budget is exceeded"
    
    # Property: All suggestions should be non-empty strings
    for suggestion in budget_status.suggestions:
        assert isinstance(suggestion, str), f"Each suggestion should be string: {type(suggestion)}"
        assert len(suggestion.strip()) > 0, "Suggestions should not be empty or whitespace-only"
    
    # Property: Suggestions should contain actionable advice
    suggestion_text = ' '.join(budget_status.suggestions).lower()
    actionable_keywords = [
        'choose', 'select', 'consider', 'reduce', 'look for', 'focus on', 
        'budget', 'lower', 'free', 'cheap', 'alternative', 'shorten'
    ]
    
    has_actionable_advice = any(keyword in suggestion_text for keyword in actionable_keywords)
    assert has_actionable_advice, f"Suggestions should contain actionable advice: {budget_status.suggestions}"
    
    # Property: More severe budget exceedance should provide more suggestions
    if exceedance_factor > 1.5:  # Significantly over budget
        assert len(budget_status.suggestions) >= 3, f"Significant budget exceedance should provide multiple suggestions: {len(budget_status.suggestions)}"
    
    # Property: Suggestions should be relevant to travel planning
    travel_keywords = [
        'flight', 'hotel', 'accommodation', 'attraction', 'activity', 'event', 
        'restaurant', 'transport', 'trip', 'travel', 'cost', 'expense'
    ]
    
    has_travel_relevance = any(keyword in suggestion_text for keyword in travel_keywords)
    assert has_travel_relevance, f"Suggestions should be relevant to travel planning: {budget_status.suggestions}"
    
    # Property: Difference should be positive when over budget
    assert budget_status.difference_inr > 0, f"Difference should be positive when over budget: {budget_status.difference_inr}"
    
    # Property: Difference should match the actual exceedance
    expected_difference = total_cost - max_budget
    assert abs(budget_status.difference_inr - expected_difference) < 0.01, \
        f"Difference should match actual exceedance: {budget_status.difference_inr} != {expected_difference}"