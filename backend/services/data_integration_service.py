"""
Data Integration Service for SERP API integration.

This service handles all external API calls to SERP API for fetching real-time travel data
including flights, hotels, attractions, events, and weather information.
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import date
import logging

from config import settings
from models.travel_data import (
    FlightData, HotelData, AttractionData, EventData, WeatherData, DateRange
)
from models.trip_preferences import BudgetLevel
from services.currency_service import CurrencyService

logger = logging.getLogger(__name__)


class DataIntegrationService:
    """Service for integrating with SERP API to fetch real-time travel data."""
    
    def __init__(self):
        self.api_key = settings.SERP_API_KEY
        self.base_url = settings.SERP_API_BASE_URL
        self.session = requests.Session()
        self.currency_service = CurrencyService()
        
        if not self.api_key:
            logger.warning("SERP API key not configured")
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to SERP API with common parameters.
        
        Args:
            params: API-specific parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            requests.RequestException: If API request fails
        """
        # Add common parameters
        params.update({
            'api_key': self.api_key,
            'output': 'json'
        })
        
        try:
            response = self.session.get(f"{self.base_url}/search", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"SERP API request failed: {e}")
            raise
    
    def fetch_flights(self, destination: str, dates: DateRange, departure_city: str = "Delhi") -> FlightData:
        """
        Fetch flight data using Google Flights API via SERP.
        
        Args:
            destination: Destination city/airport
            dates: Travel date range
            departure_city: Departure city (default: Delhi)
            
        Returns:
            FlightData object with flight information
        """
        params = {
            'engine': 'google_flights',
            'departure_id': departure_city,
            'arrival_id': destination,
            'outbound_date': dates.start_date.strftime('%Y-%m-%d'),
            'return_date': dates.end_date.strftime('%Y-%m-%d'),
            'currency': 'INR',
            'hl': 'en'
        }
        
        try:
            response = self._make_request(params)
            flight_data = FlightData.from_serp_response(response)
            
            # Convert prices to INR
            converted_response = self._convert_prices_to_inr(response, 'flights')
            flight_data = FlightData.from_serp_response(converted_response)
            
            return flight_data
        except Exception as e:
            logger.error(f"Failed to fetch flight data: {e}")
            # Return empty flight data on error
            return FlightData(flights=[], total_results=0, search_metadata={})
    
    def fetch_hotels(self, destination: str, budget: BudgetLevel, dates: DateRange) -> HotelData:
        """
        Fetch hotel data using Google Hotels API via SERP.
        
        Args:
            destination: Destination city
            budget: Budget preference level
            dates: Travel date range
            
        Returns:
            HotelData object with hotel information
        """
        # Map budget levels to price ranges (in INR)
        budget_mapping = {
            BudgetLevel.LOW: {'min_price': 0, 'max_price': 3000},
            BudgetLevel.MEDIUM: {'min_price': 3000, 'max_price': 8000},
            BudgetLevel.HIGH: {'min_price': 8000, 'max_price': 50000}
        }
        
        price_range = budget_mapping.get(budget, budget_mapping[BudgetLevel.MEDIUM])
        
        params = {
            'engine': 'google_hotels',
            'q': f"hotels in {destination}",
            'check_in_date': dates.start_date.strftime('%Y-%m-%d'),
            'check_out_date': dates.end_date.strftime('%Y-%m-%d'),
            'adults': '2',
            'currency': 'INR',
            'min_price': price_range['min_price'],
            'max_price': price_range['max_price'],
            'sort_by': '8'  # Sort by rating
        }
        
        try:
            response = self._make_request(params)
            
            # Convert prices to INR
            converted_response = self._convert_prices_to_inr(response, 'hotels')
            hotel_data = HotelData.from_serp_response(converted_response)
            
            return hotel_data
        except Exception as e:
            logger.error(f"Failed to fetch hotel data: {e}")
            # Return empty hotel data on error
            return HotelData(hotels=[], total_results=0, search_metadata={})
    
    def fetch_attractions(self, destination: str, interests: List[str]) -> AttractionData:
        """
        Fetch attraction data using Google Maps API via SERP.
        
        Args:
            destination: Destination city
            interests: List of user interests
            
        Returns:
            AttractionData object with attraction information
        """
        # Map interests to search terms
        interest_mapping = {
            'nature': 'parks nature reserves gardens',
            'food': 'restaurants local cuisine food tours',
            'adventure': 'adventure sports activities outdoor',
            'culture': 'museums cultural sites historical places',
            'shopping': 'shopping malls markets bazaars',
            'nightlife': 'bars clubs nightlife entertainment'
        }
        
        # Build search query based on interests
        search_terms = []
        for interest in interests:
            if interest in interest_mapping:
                search_terms.append(interest_mapping[interest])
        
        query = f"tourist attractions {destination}"
        if search_terms:
            query += f" {' '.join(search_terms)}"
        
        params = {
            'engine': 'google_maps',
            'q': query,
            'type': 'search',
            'hl': 'en'
        }
        
        try:
            response = self._make_request(params)
            
            # Convert prices to INR
            converted_response = self._convert_prices_to_inr(response, 'attractions')
            attraction_data = AttractionData.from_serp_response(converted_response)
            
            return attraction_data
        except Exception as e:
            logger.error(f"Failed to fetch attraction data: {e}")
            # Return empty attraction data on error
            return AttractionData(attractions=[], total_results=0, search_metadata={})
    
    def fetch_events(self, destination: str, dates: DateRange) -> EventData:
        """
        Fetch event data using Google Local Places API via SERP.
        
        Args:
            destination: Destination city
            dates: Travel date range
            
        Returns:
            EventData object with event information
        """
        params = {
            'engine': 'google_events',
            'q': f"events in {destination}",
            'start_date': dates.start_date.strftime('%Y-%m-%d'),
            'end_date': dates.end_date.strftime('%Y-%m-%d'),
            'hl': 'en'
        }
        
        try:
            response = self._make_request(params)
            
            # Convert prices to INR
            converted_response = self._convert_prices_to_inr(response, 'events')
            event_data = EventData.from_serp_response(converted_response)
            
            return event_data
        except Exception as e:
            logger.error(f"Failed to fetch event data: {e}")
            # Return empty event data on error
            return EventData(events=[], total_results=0, search_metadata={})
    
    def fetch_weather(self, destination: str, dates: DateRange) -> WeatherData:
        """
        Fetch weather data using SERP API weather engine.
        
        Args:
            destination: Destination city
            dates: Travel date range
            
        Returns:
            WeatherData object with weather information
        """
        params = {
            'engine': 'google',
            'q': f"weather in {destination}",
            'hl': 'en'
        }
        
        try:
            response = self._make_request(params)
            
            # Extract weather information from Google search results
            weather_info = {}
            forecast = []
            
            # Look for weather box in search results
            if 'answer_box' in response:
                answer_box = response['answer_box']
                if 'weather' in answer_box.get('type', '').lower():
                    weather_info = answer_box
            
            # Look for forecast information
            if 'knowledge_graph' in response:
                kg = response['knowledge_graph']
                if 'weather' in kg.get('type', '').lower():
                    forecast = kg.get('forecast', [])
            
            return WeatherData(
                current_weather=weather_info,
                forecast=forecast,
                location=destination,
                search_metadata=response.get('search_metadata', {})
            )
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            # Return empty weather data on error
            return WeatherData(
                current_weather={},
                forecast=[],
                location=destination,
                search_metadata={}
            )
    
    def fetch_all_travel_data(
        self, 
        destination: str, 
        dates: DateRange, 
        budget: BudgetLevel, 
        interests: List[str],
        departure_city: str = "Delhi"
    ) -> Dict[str, Any]:
        """
        Fetch all travel data in a single call.
        
        Args:
            destination: Destination city
            dates: Travel date range
            budget: Budget preference level
            interests: List of user interests
            departure_city: Departure city
            
        Returns:
            Dictionary containing all travel data
        """
        try:
            flights = self.fetch_flights(destination, dates, departure_city)
            hotels = self.fetch_hotels(destination, budget, dates)
            attractions = self.fetch_attractions(destination, interests)
            events = self.fetch_events(destination, dates)
            weather = self.fetch_weather(destination, dates)
            
            return {
                'flights': flights,
                'hotels': hotels,
                'attractions': attractions,
                'events': events,
                'weather': weather
            }
        except Exception as e:
            logger.error(f"Failed to fetch all travel data: {e}")
            raise
    
    def _convert_prices_to_inr(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Convert all price fields in data to INR.
        
        Args:
            data: Data containing price fields
            data_type: Type of data (flights, hotels, attractions, events)
            
        Returns:
            Data with prices converted to INR
        """
        if not data:
            return data
        
        try:
            converted_data = data.copy()
            
            if data_type == 'flights':
                # Convert flight prices
                for flight_list in ['best_flights', 'other_flights']:
                    if flight_list in converted_data:
                        for flight in converted_data[flight_list]:
                            if 'price' in flight:
                                # Assume USD if no currency specified
                                inr_price = self.currency_service.convert_to_inr(flight['price'], 'USD')
                                flight['price'] = inr_price
                                flight['price_formatted'] = self.currency_service.format_inr_price(inr_price)
            
            elif data_type == 'hotels':
                # Convert hotel prices
                if 'properties' in converted_data:
                    for hotel in converted_data['properties']:
                        if 'rate_per_night' in hotel:
                            rate_info = hotel['rate_per_night']
                            if 'extracted_lowest' in rate_info:
                                # Check if price is already in INR by looking at the formatted string
                                lowest_str = rate_info.get('lowest', '')
                                if '₹' in lowest_str or 'INR' in lowest_str.upper():
                                    # Price is already in INR, no conversion needed
                                    inr_price = rate_info['extracted_lowest']
                                else:
                                    # Assume USD if no currency specified
                                    inr_price = self.currency_service.convert_to_inr(rate_info['extracted_lowest'], 'USD')
                                
                                rate_info['extracted_lowest'] = inr_price
                                rate_info['lowest'] = self.currency_service.format_inr_price(inr_price)
                        
                        if 'total_rate' in hotel:
                            total_info = hotel['total_rate']
                            if 'extracted_lowest' in total_info:
                                # Check if price is already in INR by looking at the formatted string
                                lowest_str = total_info.get('lowest', '')
                                if '₹' in lowest_str or 'INR' in lowest_str.upper():
                                    # Price is already in INR, no conversion needed
                                    inr_price = total_info['extracted_lowest']
                                else:
                                    # Assume USD if no currency specified
                                    inr_price = self.currency_service.convert_to_inr(total_info['extracted_lowest'], 'USD')
                                
                                total_info['extracted_lowest'] = inr_price
                                total_info['lowest'] = self.currency_service.format_inr_price(inr_price)
            
            elif data_type == 'attractions':
                # Convert attraction entry fees if present
                if 'local_results' in converted_data:
                    for attraction in converted_data['local_results']:
                        if 'price' in attraction:
                            # Try to extract and convert price
                            inr_price = self.currency_service.extract_and_convert_price(str(attraction['price']))
                            if inr_price:
                                attraction['price_inr'] = inr_price
                                attraction['price_formatted'] = self.currency_service.format_inr_price(inr_price)
            
            elif data_type == 'events':
                # Convert event ticket prices if present
                if 'events_results' in converted_data:
                    for event in converted_data['events_results']:
                        if 'ticket_info' in event:
                            for ticket in event['ticket_info']:
                                if 'price' in ticket:
                                    # Try to extract and convert price
                                    inr_price = self.currency_service.extract_and_convert_price(str(ticket['price']))
                                    if inr_price:
                                        ticket['price_inr'] = inr_price
                                        ticket['price_formatted'] = self.currency_service.format_inr_price(inr_price)
            
            return converted_data
            
        except Exception as e:
            logger.error(f"Error converting prices to INR: {e}")
            return data  # Return original data if conversion fails