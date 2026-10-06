"""
Trip Planning Service for the AI Trip Planner.

This service handles itinerary generation, activity selection based on user interests,
weather integration, and daily cost calculations. It orchestrates data from multiple
sources to create comprehensive day-by-day trip plans.
"""

import uuid
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import logging

from models.trip_preferences import TripPreferences, TravelType, BudgetLevel, Interest
from models.travel_data import TripData
from models.cost_models import CostBreakdown, BudgetStatus
from models.itinerary_models import (
    Itinerary, DayPlan, Activity, ActivityType, WeatherInfo, TripPlan
)
from services.data_integration_service import DataIntegrationService
from services.cost_calculation_service import CostCalculationService
from services.ai_content_service import AIContentService

logger = logging.getLogger(__name__)


class TripPlanningService:
    """Service for generating comprehensive trip plans and itineraries."""
    
    def __init__(self):
        """Initialize the trip planning service with required dependencies."""
        self.data_service = DataIntegrationService()
        self.cost_service = CostCalculationService()
        self.ai_service = AIContentService()
        
        # Activity selection preferences by travel type
        self.travel_type_preferences = {
            TravelType.SOLO: {
                'max_activities_per_day': 4,
                'preferred_duration': 2.5,
                'activity_types': ['culture', 'nature', 'food']
            },
            TravelType.FRIENDS: {
                'max_activities_per_day': 5,
                'preferred_duration': 3.0,
                'activity_types': ['adventure', 'nightlife', 'food', 'events']
            },
            TravelType.FAMILY: {
                'max_activities_per_day': 3,
                'preferred_duration': 2.0,
                'activity_types': ['nature', 'culture', 'family-friendly']
            },
            TravelType.COUPLE: {
                'max_activities_per_day': 4,
                'preferred_duration': 2.5,
                'activity_types': ['culture', 'food', 'nature', 'romantic']
            }
        }
        
        # Budget-based activity filtering
        self.budget_activity_limits = {
            BudgetLevel.LOW: {'max_cost_per_activity': 500, 'max_daily_activities': 3},
            BudgetLevel.MEDIUM: {'max_cost_per_activity': 1500, 'max_daily_activities': 4},
            BudgetLevel.HIGH: {'max_cost_per_activity': 5000, 'max_daily_activities': 6}
        }
    
    def create_trip_plan(self, preferences: TripPreferences) -> TripPlan:
        """
        Create a complete trip plan with itinerary and cost breakdown.
        
        Args:
            preferences: User trip preferences
            
        Returns:
            TripPlan: Complete trip plan with itinerary and costs
        """
        try:
            # Generate unique trip ID
            trip_id = str(uuid.uuid4())
            
            # Fetch all travel data
            trip_data = self._fetch_trip_data(preferences)
            
            # Generate itinerary
            itinerary = self.generate_itinerary(trip_data, preferences, trip_id)
            
            # Calculate costs
            cost_breakdown = self.cost_service.calculate_trip_costs(trip_data, preferences)
            
            # Calculate budget status
            budget_status = self.cost_service.calculate_budget_status(
                cost_breakdown, preferences.max_budget_inr
            )
            
            # Create complete trip plan
            trip_plan = TripPlan(
                id=trip_id,
                user_id="",  # Will be set by calling service
                preferences=preferences,
                itinerary=itinerary,
                cost_breakdown=cost_breakdown,
                budget_status=budget_status
            )
            
            return trip_plan
            
        except Exception as e:
            logger.error(f"Error creating trip plan: {e}")
            raise
    
    def generate_itinerary(self, trip_data: TripData, preferences: TripPreferences, trip_id: str) -> Itinerary:
        """
        Generate a day-by-day itinerary based on trip data and preferences.
        
        Args:
            trip_data: Combined travel data from SERP API
            preferences: User trip preferences
            trip_id: Unique trip identifier
            
        Returns:
            Itinerary: Complete day-by-day itinerary
        """
        try:
            logger.info(f"Generating itinerary for {preferences.travel_days} days from {preferences.start_date} to {preferences.end_date}")
            days = []
            current_date = preferences.start_date
            
            # Get travel type preferences
            travel_prefs = self.travel_type_preferences.get(
                preferences.travel_type, 
                self.travel_type_preferences[TravelType.SOLO]
            )
            
            # Get budget constraints
            budget_limits = self.budget_activity_limits.get(
                preferences.budget_preference,
                self.budget_activity_limits[BudgetLevel.MEDIUM]
            )
            
            # Select activities based on interests
            selected_activities = self._select_activities_by_interests(
                trip_data, preferences.interests, preferences.travel_days,
                travel_prefs, budget_limits
            )
            
            # Get flight and hotel activities
            flight_activities = self._get_flight_activities(trip_data)
            hotel_activities = self._get_hotel_activities(trip_data, preferences.travel_days)
            
            logger.info(f"Flight activities: {len(flight_activities)}")
            logger.info(f"Hotel activities: {len(hotel_activities)}")
            
            # Generate day plans
            for day_num in range(preferences.travel_days):
                # Get weather for this day
                weather = self._get_weather_for_date(trip_data.weather, current_date)
                
                # Select activities for this day
                day_activities = self._select_daily_activities(
                    selected_activities, day_num, travel_prefs, budget_limits
                )
                
                logger.info(f"Day {day_num + 1} base activities: {len(day_activities)}")
                
                # Add flight activities for first and last day
                if day_num == 0 and flight_activities.get('outbound'):
                    day_activities.insert(0, flight_activities['outbound'])
                    logger.info(f"Added outbound flight to day {day_num + 1}")
                elif day_num == preferences.travel_days - 1 and flight_activities.get('return'):
                    day_activities.append(flight_activities['return'])
                    logger.info(f"Added return flight to day {day_num + 1}")
                
                # Add hotel activity for each night (except last day)
                if day_num < preferences.travel_days - 1 and hotel_activities:
                    # Select hotel for this night (rotate through available hotels)
                    hotel_activity = hotel_activities[day_num % len(hotel_activities)]
                    day_activities.append(hotel_activity)
                    logger.info(f"Added hotel activity to day {day_num + 1}: {hotel_activity.name}")
                
                logger.info(f"Day {day_num + 1} final activities: {len(day_activities)}")
                
                # Calculate daily cost
                daily_cost = sum(activity.cost_inr for activity in day_activities)
                
                # Create day plan
                day_plan = DayPlan(
                    day_number=day_num + 1,
                    date=current_date,
                    activities=day_activities,
                    weather=weather,
                    daily_cost_inr=daily_cost
                )
                
                days.append(day_plan)
                current_date += timedelta(days=1)
            
            # Calculate total cost
            total_cost = sum(day.daily_cost_inr for day in days)
            
            return Itinerary(
                trip_id=trip_id,
                days=days,
                total_cost_inr=total_cost
            )
            
        except Exception as e:
            logger.error(f"Error generating itinerary: {e}")
            raise
    
    def _fetch_trip_data(self, preferences: TripPreferences) -> TripData:
        """Fetch all required travel data for trip planning."""
        from models.travel_data import DateRange
        
        date_range = DateRange(preferences.start_date, preferences.end_date)
        interests_str = [interest.value for interest in preferences.interests]
        
        # Fetch all travel data
        flights = self.data_service.fetch_flights(preferences.destination, date_range)
        hotels = self.data_service.fetch_hotels(preferences.destination, preferences.budget_preference, date_range)
        attractions = self.data_service.fetch_attractions(preferences.destination, interests_str)
        events = self.data_service.fetch_events(preferences.destination, date_range)
        weather = self.data_service.fetch_weather(preferences.destination, date_range)
        
        return TripData(
            flights=flights,
            hotels=hotels,
            attractions=attractions,
            events=events,
            weather=weather
        )
    
    def _select_activities_by_interests(
        self, 
        trip_data: TripData, 
        interests: List[Interest],
        travel_days: int,
        travel_prefs: Dict[str, Any],
        budget_limits: Dict[str, Any]
    ) -> List[Activity]:
        """
        Select activities based on user interests and constraints.
        
        Args:
            trip_data: Available travel data
            interests: User interests
            travel_days: Number of travel days
            travel_prefs: Travel type preferences
            budget_limits: Budget constraints
            
        Returns:
            List[Activity]: Selected activities for the trip
        """
        activities = []
        interest_values = [interest.value for interest in interests]
        
        # Process attractions
        if trip_data.attractions and trip_data.attractions.attractions:
            for attraction in trip_data.attractions.attractions:
                if self._matches_interests(attraction, interest_values):
                    # Generate AI description
                    description = self.ai_service.generate_attraction_description(attraction)
                    activity = Activity.from_attraction_data(attraction, description)
                    
                    # Check budget constraints
                    if activity.cost_inr <= budget_limits['max_cost_per_activity']:
                        activities.append(activity)
        
        # Process events
        if trip_data.events and trip_data.events.events:
            for event in trip_data.events.events:
                if self._matches_interests(event, interest_values):
                    # Generate AI description
                    description = self.ai_service.generate_event_description(event)
                    activity = Activity.from_event_data(event, description)
                    
                    # Check budget constraints
                    if activity.cost_inr <= budget_limits['max_cost_per_activity']:
                        activities.append(activity)
        
        # Sort activities by rating and cost
        activities.sort(key=lambda x: (float(x.rating) if x.rating and str(x.rating).replace('.', '').isdigit() else 0, -x.cost_inr), reverse=True)
        
        # Limit total activities based on travel days and preferences
        max_total_activities = travel_days * travel_prefs['max_activities_per_day']
        return activities[:max_total_activities]
    
    def _matches_interests(self, item: Dict[str, Any], interests: List[str]) -> bool:
        """Check if an attraction or event matches user interests."""
        item_text = (
            item.get('title', '') + ' ' + 
            item.get('snippet', '') + ' ' + 
            item.get('description', '') + ' ' +
            ' '.join(item.get('types', []))
        ).lower()
        
        # Interest keyword mapping
        interest_keywords = {
            'nature': ['park', 'garden', 'nature', 'outdoor', 'hiking', 'wildlife', 'beach', 'mountain'],
            'food': ['restaurant', 'food', 'cuisine', 'dining', 'cafe', 'market', 'cooking', 'culinary'],
            'adventure': ['adventure', 'sport', 'climbing', 'diving', 'safari', 'extreme', 'thrill'],
            'culture': ['museum', 'cultural', 'heritage', 'historical', 'art', 'temple', 'monument'],
            'shopping': ['shopping', 'mall', 'market', 'bazaar', 'store', 'boutique', 'souvenir'],
            'nightlife': ['bar', 'club', 'nightlife', 'entertainment', 'music', 'dance', 'pub']
        }
        
        # Check if any interest keywords match
        for interest in interests:
            if interest in interest_keywords:
                keywords = interest_keywords[interest]
                if any(keyword in item_text for keyword in keywords):
                    return True
        
        return len(interests) == 0  # If no specific interests, include all
    
    def _select_daily_activities(
        self, 
        all_activities: List[Activity], 
        day_number: int,
        travel_prefs: Dict[str, Any],
        budget_limits: Dict[str, Any]
    ) -> List[Activity]:
        """Select activities for a specific day."""
        max_activities = min(
            travel_prefs['max_activities_per_day'],
            budget_limits['max_daily_activities']
        )
        
        # Simple round-robin distribution: cycle through activities
        # This ensures all days get activities even if we have fewer activities than days
        selected = []
        activity_index = day_number
        
        while len(selected) < max_activities and activity_index < len(all_activities):
            selected.append(all_activities[activity_index])
            activity_index += 1  # Move to next activity for this day
            
            # If we've used all activities, start from beginning (cycle through)
            if activity_index >= len(all_activities) and len(selected) < max_activities:
                break
        
        return selected
    
    def _get_weather_for_date(self, weather_data, target_date: date) -> WeatherInfo:
        """Get weather information for a specific date."""
        if not weather_data:
            return WeatherInfo(date=target_date, condition="Unknown")
        
        weather_dict = {
            'current_weather': weather_data.current_weather,
            'forecast': weather_data.forecast
        }
        
        return WeatherInfo.from_weather_data(weather_dict, target_date)
    
    def _get_flight_activities(self, trip_data: TripData) -> Dict[str, Activity]:
        """Extract flight activities from trip data."""
        flight_activities = {}
        
        logger.info(f"Processing flight data: {trip_data.flights}")
        
        if not trip_data.flights or not trip_data.flights.flights:
            logger.warning("No flight data available")
            return flight_activities
        
        # Get the best flight options (first flight in the list)
        flights = trip_data.flights.flights
        logger.info(f"Found {len(flights)} flights")
        
        if flights:
            best_flight = flights[0]  # Assume first flight is the best option
            logger.info(f"Best flight data: {best_flight}")
            
            # Create outbound flight activity
            if 'outbound' in best_flight or 'departure' in str(best_flight).lower():
                outbound_data = best_flight.copy()
                outbound_data['flight_type'] = 'outbound'
                flight_activities['outbound'] = Activity.from_flight_data(outbound_data, 'outbound')
                logger.info("Created outbound flight activity")
            
            # Create return flight activity (if round trip)
            if len(flights) > 1:
                return_flight = flights[1] if len(flights) > 1 else best_flight.copy()
                return_data = return_flight.copy()
                return_data['flight_type'] = 'return'
                flight_activities['return'] = Activity.from_flight_data(return_data, 'return')
                logger.info("Created return flight activity")
            elif 'return' in best_flight or 'round_trip' in str(best_flight).lower():
                # Single flight object with return info
                return_data = best_flight.copy()
                return_data['flight_type'] = 'return'
                flight_activities['return'] = Activity.from_flight_data(return_data, 'return')
                logger.info("Created return flight activity from single flight")
        
        logger.info(f"Created {len(flight_activities)} flight activities")
        return flight_activities
    
    def _get_hotel_activities(self, trip_data: TripData, travel_days: int) -> List[Activity]:
        """Extract hotel activities from trip data."""
        hotel_activities = []
        
        logger.info(f"Processing hotel data: {trip_data.hotels}")
        
        if not trip_data.hotels or not trip_data.hotels.hotels:
            logger.warning("No hotel data available")
            return hotel_activities
        
        # Get available hotels
        hotels = trip_data.hotels.hotels
        logger.info(f"Found {len(hotels)} hotels")
        
        # Create hotel activities for each night (travel_days - 1 nights)
        nights_needed = max(1, travel_days - 1)
        logger.info(f"Need {nights_needed} nights of accommodation")
        
        for i in range(min(nights_needed, len(hotels))):
            hotel = hotels[i]
            logger.info(f"Creating hotel activity for hotel {i}: {hotel}")
            hotel_activity = Activity.from_hotel_data(hotel)
            hotel_activities.append(hotel_activity)
        
        # If we need more nights than available hotels, repeat the best hotel
        if nights_needed > len(hotels) and hotels:
            best_hotel = hotels[0]  # Assume first hotel is the best
            for i in range(len(hotels), nights_needed):
                logger.info(f"Repeating best hotel for night {i}")
                hotel_activity = Activity.from_hotel_data(best_hotel)
                hotel_activities.append(hotel_activity)
        
        logger.info(f"Created {len(hotel_activities)} hotel activities")
        return hotel_activities
    
    def save_trip_plan(self, user_id: str, trip_plan: TripPlan) -> str:
        """
        Save trip plan to database (placeholder for database integration).
        
        Args:
            user_id: User identifier
            trip_plan: Complete trip plan to save
            
        Returns:
            str: Saved trip plan ID
        """
        # TODO: Implement database persistence
        # This will be implemented in task 10 (Data persistence with Supabase)
        trip_plan.user_id = user_id
        logger.info(f"Trip plan {trip_plan.id} saved for user {user_id}")
        return trip_plan.id
    
    def get_saved_trips(self, user_id: str) -> List[TripPlan]:
        """
        Retrieve saved trip plans for a user (placeholder for database integration).
        
        Args:
            user_id: User identifier
            
        Returns:
            List[TripPlan]: List of saved trip plans
        """
        # TODO: Implement database retrieval
        # This will be implemented in task 10 (Data persistence with Supabase)
        logger.info(f"Retrieving saved trips for user {user_id}")
        return []