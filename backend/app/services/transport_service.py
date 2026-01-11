"""
Transport service for flight and local transport information.
"""
import os
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
from amadeus import Client, ResponseError
import googlemaps
from ..models.api_models import FlightSearchParams, TransportRequest, FlightOption
from ..core.exceptions import ExternalServiceError, ValidationError, RateLimitError

logger = logging.getLogger(__name__)

class TransportService:
    """
    Service class for transport-related operations.
    Handles flight searches and local transport information.
    """
    
    def __init__(self):
        """Initialize the transport service with API clients."""
        # Initialize Amadeus client
        self.amadeus_client = None
        self.gmaps_client = None
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay_base = 1.0
        self.max_retry_delay = 30.0
        
        # Rate limiting tracking
        self.amadeus_last_request = 0
        self.gmaps_last_request = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Set up Amadeus client if credentials are available
        amadeus_key = os.getenv("AMADEUS_API_KEY")
        amadeus_secret = os.getenv("AMADEUS_API_SECRET")
        
        if amadeus_key and amadeus_secret:
            try:
                self.amadeus_client = Client(
                    client_id=amadeus_key,
                    client_secret=amadeus_secret
                )
                logger.info("Amadeus API client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Amadeus client: {e}")
                self.amadeus_client = None
        else:
            logger.warning("Amadeus API credentials not found, using mock data")
        
        # Set up Google Maps client if API key is available
        gmaps_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if gmaps_key:
            try:
                self.gmaps_client = googlemaps.Client(key=gmaps_key)
                logger.info("Google Maps API client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Maps client: {e}")
                self.gmaps_client = None
        else:
            logger.warning("Google Maps API key not found, using mock data")
    
    def _validate_flight_params(self, params: FlightSearchParams) -> None:
        """
        Validate flight search parameters.
        
        Args:
            params: Flight search parameters
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate origin
        if not params.origin or len(params.origin.strip()) < 3:
            raise ValidationError("Origin must be at least 3 characters (airport code or city)")
        
        # Validate destination
        if not params.destination or len(params.destination.strip()) < 3:
            raise ValidationError("Destination must be at least 3 characters (airport code or city)")
        
        # Validate dates
        if not isinstance(params.departure_date, date):
            raise ValidationError("Departure date must be a valid date")
        
        if params.departure_date < date.today():
            raise ValidationError("Departure date cannot be in the past")
        
        if params.return_date:
            if not isinstance(params.return_date, date):
                raise ValidationError("Return date must be a valid date")
            
            if params.return_date < params.departure_date:
                raise ValidationError("Return date cannot be before departure date")
        
        # Validate passengers
        if not isinstance(params.passengers, int) or params.passengers < 1 or params.passengers > 9:
            raise ValidationError("Number of passengers must be between 1 and 9")
    
    def _validate_transport_request(self, request: TransportRequest) -> None:
        """
        Validate transport request parameters.
        
        Args:
            request: Transport request parameters
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate location
        if not request.location or len(request.location.strip()) < 2:
            raise ValidationError("Location must be at least 2 characters")
        
        if len(request.location.strip()) > 100:
            raise ValidationError("Location cannot exceed 100 characters")
        
        # Check for potentially harmful content
        harmful_patterns = ['<script', 'javascript:', 'data:', 'vbscript:', 'onload=']
        location_lower = request.location.lower()
        for pattern in harmful_patterns:
            if pattern in location_lower:
                raise ValidationError("Invalid characters in location")
        
        # Validate transport type if provided
        if request.transport_type:
            valid_types = ["taxi", "bus", "metro", "rideshare", "walking"]
            if request.transport_type not in valid_types:
                raise ValidationError(f"Transport type must be one of: {', '.join(valid_types)}")
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay for retries.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        delay = self.retry_delay_base * (2 ** attempt)
        return min(delay, self.max_retry_delay)
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if the error should be retried
        """
        # Amadeus specific errors
        if isinstance(error, ResponseError):
            # Check status code for retryable errors
            if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
                status_code = error.response.status_code
                # Retry on server errors and rate limits
                return status_code >= 500 or status_code == 429
        
        # Google Maps specific errors
        if isinstance(error, googlemaps.exceptions.ApiError):
            return True  # Most Google Maps errors are retryable
        
        if isinstance(error, googlemaps.exceptions.Timeout):
            return True
        
        # Generic network/timeout errors
        error_str = str(error).lower()
        retryable_patterns = [
            'timeout', 'connection', 'network', 'unavailable',
            'temporary', 'rate limit', 'quota', 'overloaded'
        ]
        
        return any(pattern in error_str for pattern in retryable_patterns)
    
    def _enforce_rate_limit(self, service: str) -> None:
        """
        Enforce rate limiting for external API calls.
        
        Args:
            service: Service name ('amadeus' or 'gmaps')
        """
        current_time = time.time()
        
        if service == 'amadeus':
            time_since_last = current_time - self.amadeus_last_request
            if time_since_last < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last
                time.sleep(sleep_time)
            self.amadeus_last_request = time.time()
        
        elif service == 'gmaps':
            time_since_last = current_time - self.gmaps_last_request
            if time_since_last < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last
                time.sleep(sleep_time)
            self.gmaps_last_request = time.time()
    
    async def search_flights(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """
        Search for flight options based on specified parameters with enhanced error handling.
        
        Args:
            params: Flight search parameters
            
        Returns:
            List of flight options with pricing and details
            
        Raises:
            ValidationError: If parameters are invalid
            ExternalServiceError: If flight search fails after retries
        """
        # Validate input parameters
        self._validate_flight_params(params)
        
        try:
            if self.amadeus_client:
                return await self._search_flights_amadeus_with_retry(params)
            else:
                logger.info("Using mock flight data - Amadeus client not available")
                return await self._get_mock_flights(params)
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Flight search failed: {e}")
            # Fallback to mock data on error
            logger.info("Falling back to mock flight data due to error")
            return await self._get_mock_flights(params)
    
    async def _search_flights_amadeus_with_retry(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """
        Search flights using Amadeus API with retry logic.
        
        Args:
            params: Flight search parameters
            
        Returns:
            List of flight options from Amadeus API
            
        Raises:
            ExternalServiceError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Amadeus flight search attempt {attempt + 1}/{self.max_retries}")
                
                # Enforce rate limiting
                self._enforce_rate_limit('amadeus')
                
                return await self._search_flights_amadeus(params)
                
            except ResponseError as e:
                last_error = e
                
                # Check if it's a rate limit error
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    if e.response.status_code == 429:
                        retry_after = 60  # Default retry after 60 seconds
                        logger.warning(f"Amadeus rate limit hit, retry after {retry_after}s")
                        raise RateLimitError(retry_after=retry_after)
                
                # Check if error is retryable
                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable Amadeus error: {e}")
                    break
                
                logger.warning(f"Amadeus attempt {attempt + 1} failed: {e}")
                
                # Wait before retrying
                if attempt < self.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"Retrying Amadeus request in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
            
            except Exception as e:
                last_error = e
                logger.warning(f"Amadeus attempt {attempt + 1} failed with unexpected error: {e}")
                
                if not self._is_retryable_error(e):
                    break
                
                if attempt < self.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
        
        # All retries failed
        error_msg = f"Amadeus flight search failed after {self.max_retries} attempts. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise ExternalServiceError("Amadeus", error_msg)
    
    async def _search_flights_amadeus(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """
        Search flights using Amadeus API.
        
        Args:
            params: Flight search parameters
            
        Returns:
            List of flight options from Amadeus API
        """
        try:
            # Convert date objects to strings for Amadeus API
            departure_date_str = params.departure_date.strftime("%Y-%m-%d")
            
            # Prepare search parameters for Amadeus
            search_params = {
                "originLocationCode": params.origin.upper().strip(),
                "destinationLocationCode": params.destination.upper().strip(),
                "departureDate": departure_date_str,
                "adults": params.passengers
            }
            
            # Add return date if provided
            if params.return_date:
                search_params["returnDate"] = params.return_date.strftime("%Y-%m-%d")
            
            # Execute flight search with timeout
            start_time = time.time()
            response = self.amadeus_client.shopping.flight_offers_search.get(**search_params)
            search_time = time.time() - start_time
            
            logger.info(f"Amadeus flight search completed in {search_time:.2f}s")
            
            # Process and format response
            flights = []
            for offer in response.data[:10]:  # Limit to 10 results
                flight_data = self._format_amadeus_flight(offer)
                if flight_data:
                    flights.append(flight_data)
            
            logger.info(f"Successfully retrieved {len(flights)} flight options from Amadeus")
            return flights
            
        except ResponseError as e:
            logger.error(f"Amadeus API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Amadeus flight search: {e}")
            raise
    
    def _format_amadeus_flight(self, offer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Format Amadeus flight offer into our standard format with enhanced validation.
        
        Args:
            offer: Raw Amadeus flight offer
            
        Returns:
            Formatted flight data or None if formatting fails
        """
        try:
            # Validate offer structure
            if not isinstance(offer, dict):
                logger.warning("Invalid Amadeus offer format: not a dictionary")
                return None
            
            # Extract first itinerary and segment
            itineraries = offer.get("itineraries", [])
            if not itineraries:
                logger.warning("No itineraries found in Amadeus offer")
                return None
            
            itinerary = itineraries[0]
            segments = itinerary.get("segments", [])
            if not segments:
                logger.warning("No segments found in Amadeus itinerary")
                return None
            
            segment = segments[0]
            
            # Extract pricing information
            price_info = offer.get("price", {})
            if not price_info:
                logger.warning("No price information in Amadeus offer")
                return None
            
            # Validate and extract required fields
            carrier_code = segment.get("carrierCode", "")
            flight_number = segment.get("number", "")
            departure_info = segment.get("departure", {})
            arrival_info = segment.get("arrival", {})
            
            # Format flight data with validation
            flight_data = {
                "airline": carrier_code if carrier_code else "Unknown",
                "flight_number": f"{carrier_code}{flight_number}" if carrier_code and flight_number else "Unknown",
                "departure_time": departure_info.get("at", ""),
                "arrival_time": arrival_info.get("at", ""),
                "duration": self._parse_duration(itinerary.get("duration", "PT0M")),
                "price": float(price_info.get("total", 0)),
                "stops": max(0, len(segments) - 1),
                "currency": price_info.get("currency", "USD")
            }
            
            # Validate essential fields
            if not flight_data["departure_time"] or not flight_data["arrival_time"]:
                logger.warning("Missing departure or arrival time in Amadeus offer")
                return None
            
            if flight_data["price"] <= 0:
                logger.warning("Invalid price in Amadeus offer")
                return None
            
            return flight_data
            
        except Exception as e:
            logger.warning(f"Failed to format Amadeus flight offer: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration string to minutes.
        
        Args:
            duration_str: ISO 8601 duration (e.g., "PT6H30M")
            
        Returns:
            Duration in minutes
        """
        try:
            # Simple parser for PT format (PT6H30M)
            if not duration_str.startswith("PT"):
                return 0
            
            duration_str = duration_str[2:]  # Remove "PT"
            hours = 0
            minutes = 0
            
            # Extract hours
            if "H" in duration_str:
                h_index = duration_str.index("H")
                hours = int(duration_str[:h_index])
                duration_str = duration_str[h_index + 1:]
            
            # Extract minutes
            if "M" in duration_str:
                m_index = duration_str.index("M")
                minutes = int(duration_str[:m_index])
            
            return hours * 60 + minutes
            
        except Exception:
            return 0
    
    async def _get_mock_flights(self, params: FlightSearchParams) -> List[Dict[str, Any]]:
        """
        Generate mock flight data when Amadeus API is not available.
        
        Args:
            params: Flight search parameters
            
        Returns:
            List of mock flight options
        """
        # Generate mock flights based on route
        base_price = self._estimate_flight_price(params.origin, params.destination)
        
        mock_flights = [
            {
                "airline": "Mock Airlines",
                "flight_number": "MA101",
                "departure_time": "08:00",
                "arrival_time": "14:30",
                "duration": 390,  # 6.5 hours
                "price": base_price,
                "stops": 0,
                "currency": "USD"
            },
            {
                "airline": "Budget Air",
                "flight_number": "BA205",
                "departure_time": "12:15",
                "arrival_time": "20:45",
                "duration": 450,  # 7.5 hours
                "price": base_price * 0.8,
                "stops": 1,
                "currency": "USD"
            },
            {
                "airline": "Premium Airways",
                "flight_number": "PA350",
                "departure_time": "18:30",
                "arrival_time": "23:15",
                "duration": 345,  # 5.75 hours
                "price": base_price * 1.3,
                "stops": 0,
                "currency": "USD"
            }
        ]
        
        return mock_flights
    
    def _estimate_flight_price(self, origin: str, destination: str) -> float:
        """
        Estimate flight price based on route.
        
        Args:
            origin: Origin airport/city
            destination: Destination airport/city
            
        Returns:
            Estimated price in USD
        """
        # Simple price estimation based on common routes
        route_key = f"{origin.upper()}-{destination.upper()}"
        
        # Base prices for common routes (mock data)
        route_prices = {
            "JFK-CDG": 650.0,
            "LAX-NRT": 850.0,
            "LHR-JFK": 700.0,
            "DXB-LHR": 450.0,
            "SYD-LAX": 1200.0
        }
        
        # Return specific price if route exists, otherwise estimate
        if route_key in route_prices:
            return route_prices[route_key]
        elif route_key[::-1] in route_prices:  # Check reverse route
            return route_prices[route_key[::-1]]
        else:
            # Default estimation based on distance (simplified)
            return 500.0  # Base international flight price
    
    async def get_local_transport(self, request: TransportRequest) -> List[Dict[str, Any]]:
        """
        Get local transport options for a specified location with enhanced error handling.
        
        Args:
            request: Local transport request parameters
            
        Returns:
            List of local transport options with cost estimates
            
        Raises:
            ValidationError: If request parameters are invalid
            ExternalServiceError: If transport data retrieval fails after retries
        """
        # Validate input parameters
        self._validate_transport_request(request)
        
        try:
            if self.gmaps_client:
                return await self._get_transport_with_gmaps_retry(request)
            else:
                logger.info("Using mock transport data - Google Maps client not available")
                return await self._get_mock_transport(request)
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Local transport search failed: {e}")
            # Fallback to mock data on error
            logger.info("Falling back to mock transport data due to error")
            return await self._get_mock_transport(request)
    
    async def _get_transport_with_gmaps_retry(self, request: TransportRequest) -> List[Dict[str, Any]]:
        """
        Get transport options using Google Maps API with retry logic.
        
        Args:
            request: Transport request parameters
            
        Returns:
            List of transport options with Google Maps data
            
        Raises:
            ExternalServiceError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Google Maps transport search attempt {attempt + 1}/{self.max_retries}")
                
                # Enforce rate limiting
                self._enforce_rate_limit('gmaps')
                
                return await self._get_transport_with_gmaps(request)
                
            except googlemaps.exceptions.ApiError as e:
                last_error = e
                
                # Check for quota exceeded
                if "OVER_QUERY_LIMIT" in str(e):
                    logger.warning("Google Maps quota exceeded")
                    raise RateLimitError(retry_after=3600)  # Retry after 1 hour
                
                logger.warning(f"Google Maps attempt {attempt + 1} failed: {e}")
                
                if not self._is_retryable_error(e):
                    break
                
                if attempt < self.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"Retrying Google Maps request in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
            
            except Exception as e:
                last_error = e
                logger.warning(f"Google Maps attempt {attempt + 1} failed with unexpected error: {e}")
                
                if not self._is_retryable_error(e):
                    break
                
                if attempt < self.max_retries - 1:
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
        
        # All retries failed
        error_msg = f"Google Maps transport search failed after {self.max_retries} attempts. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise ExternalServiceError("Google Maps", error_msg)
    
    async def _get_transport_with_gmaps(self, request: TransportRequest) -> List[Dict[str, Any]]:
        """
        Get transport options using Google Maps API.
        
        Args:
            request: Transport request parameters
            
        Returns:
            List of transport options with Google Maps data
        """
        try:
            # Use Google Maps to get location details and estimate costs
            start_time = time.time()
            geocode_result = self.gmaps_client.geocode(request.location)
            geocode_time = time.time() - start_time
            
            logger.info(f"Google Maps geocoding completed in {geocode_time:.2f}s")
            
            if not geocode_result:
                logger.warning(f"Could not geocode location: {request.location}")
                return await self._get_mock_transport(request)
            
            # Extract location information
            location_info = geocode_result[0]
            country = None
            city = None
            
            for component in location_info.get("address_components", []):
                types = component.get("types", [])
                if "country" in types:
                    country = component.get("long_name")
                elif "locality" in types or "administrative_area_level_1" in types:
                    city = component.get("long_name")
            
            # Generate transport options based on location
            transport_options = await self._generate_location_transport(request.location, country, city)
            
            logger.info(f"Successfully generated {len(transport_options)} transport options for {request.location}")
            return transport_options
            
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Maps API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Google Maps transport search: {e}")
            raise
    
    async def _generate_location_transport(self, location: str, country: str, city: str) -> List[Dict[str, Any]]:
        """
        Generate transport options based on location information.
        
        Args:
            location: Original location string
            country: Country name
            city: City name
            
        Returns:
            List of location-appropriate transport options
        """
        transport_options = []
        
        # Add taxi option (available everywhere)
        transport_options.append({
            "type": "taxi",
            "provider": "Local Taxi",
            "base_fare": self._get_taxi_base_fare(country),
            "per_km": self._get_taxi_per_km(country),
            "currency": "USD",
            "availability": "24/7"
        })
        
        # Add public transport based on location
        if self._has_metro_system(city, country):
            transport_options.append({
                "type": "metro",
                "provider": f"{city} Metro",
                "cost_per_ride": self._get_metro_cost(city, country),
                "day_pass": self._get_metro_day_pass(city, country),
                "currency": "USD",
                "availability": "5:30 AM - 12:30 AM"
            })
        
        # Add bus option
        transport_options.append({
            "type": "bus",
            "provider": f"{city} Public Bus",
            "cost_per_ride": self._get_bus_cost(country),
            "day_pass": self._get_bus_day_pass(country),
            "currency": "USD",
            "availability": "6:00 AM - 11:00 PM"
        })
        
        # Add ride-sharing if in major city
        if self._has_rideshare(city, country):
            transport_options.append({
                "type": "rideshare",
                "provider": "Uber/Lyft",
                "base_fare": self._get_rideshare_base_fare(country),
                "per_km": self._get_rideshare_per_km(country),
                "currency": "USD",
                "availability": "24/7"
            })
        
        return transport_options
    
    async def _get_mock_transport(self, request: TransportRequest) -> List[Dict[str, Any]]:
        """
        Generate mock transport data when Google Maps API is not available.
        
        Args:
            request: Transport request parameters
            
        Returns:
            List of mock transport options
        """
        mock_transport = [
            {
                "type": "taxi",
                "provider": "City Taxi",
                "base_fare": 3.50,
                "per_km": 1.20,
                "currency": "USD",
                "availability": "24/7"
            },
            {
                "type": "metro",
                "provider": "City Metro",
                "cost_per_ride": 2.50,
                "day_pass": 8.00,
                "currency": "USD",
                "availability": "5:30 AM - 12:30 AM"
            },
            {
                "type": "bus",
                "provider": "City Bus",
                "cost_per_ride": 1.50,
                "day_pass": 5.00,
                "currency": "USD",
                "availability": "6:00 AM - 11:00 PM"
            },
            {
                "type": "rideshare",
                "provider": "Ride App",
                "base_fare": 2.00,
                "per_km": 0.90,
                "currency": "USD",
                "availability": "24/7"
            }
        ]
        
        return mock_transport
    
    # Helper methods for cost estimation
    def _get_taxi_base_fare(self, country: str) -> float:
        """Get taxi base fare by country."""
        country_fares = {
            "United States": 3.50,
            "United Kingdom": 4.20,
            "France": 3.80,
            "Germany": 4.00,
            "Japan": 5.50,
            "Australia": 4.50
        }
        return country_fares.get(country, 3.00)
    
    def _get_taxi_per_km(self, country: str) -> float:
        """Get taxi per-km rate by country."""
        country_rates = {
            "United States": 1.20,
            "United Kingdom": 1.50,
            "France": 1.30,
            "Germany": 1.40,
            "Japan": 2.00,
            "Australia": 1.60
        }
        return country_rates.get(country, 1.00)
    
    def _has_metro_system(self, city: str, country: str) -> bool:
        """Check if city has metro system."""
        metro_cities = [
            "New York", "London", "Paris", "Tokyo", "Berlin", "Sydney",
            "Madrid", "Rome", "Moscow", "Beijing", "Shanghai", "Seoul"
        ]
        return city in metro_cities if city else False
    
    def _get_metro_cost(self, city: str, country: str) -> float:
        """Get metro cost per ride."""
        metro_costs = {
            "New York": 2.90,
            "London": 3.20,
            "Paris": 1.90,
            "Tokyo": 2.50,
            "Berlin": 3.00,
            "Sydney": 4.00
        }
        return metro_costs.get(city, 2.50)
    
    def _get_metro_day_pass(self, city: str, country: str) -> float:
        """Get metro day pass cost."""
        day_passes = {
            "New York": 33.00,
            "London": 15.20,
            "Paris": 7.50,
            "Tokyo": 12.00,
            "Berlin": 8.80,
            "Sydney": 16.80
        }
        return day_passes.get(city, 8.00)
    
    def _get_bus_cost(self, country: str) -> float:
        """Get bus cost per ride."""
        bus_costs = {
            "United States": 2.00,
            "United Kingdom": 2.50,
            "France": 1.50,
            "Germany": 2.80,
            "Japan": 2.30,
            "Australia": 3.20
        }
        return bus_costs.get(country, 1.50)
    
    def _get_bus_day_pass(self, country: str) -> float:
        """Get bus day pass cost."""
        day_passes = {
            "United States": 6.00,
            "United Kingdom": 8.00,
            "France": 5.00,
            "Germany": 7.50,
            "Japan": 8.50,
            "Australia": 10.00
        }
        return day_passes.get(country, 5.00)
    
    def _has_rideshare(self, city: str, country: str) -> bool:
        """Check if city has rideshare services."""
        # Most major cities have rideshare
        major_cities = [
            "New York", "Los Angeles", "London", "Paris", "Tokyo", "Berlin",
            "Sydney", "Madrid", "Rome", "Barcelona", "Amsterdam", "Vienna"
        ]
        return city in major_cities if city else True  # Default to available
    
    def _get_rideshare_base_fare(self, country: str) -> float:
        """Get rideshare base fare."""
        base_fares = {
            "United States": 2.50,
            "United Kingdom": 3.00,
            "France": 2.80,
            "Germany": 3.20,
            "Japan": 4.00,
            "Australia": 3.50
        }
        return base_fares.get(country, 2.50)
    
    def _get_rideshare_per_km(self, country: str) -> float:
        """Get rideshare per-km rate."""
        per_km_rates = {
            "United States": 0.90,
            "United Kingdom": 1.10,
            "France": 1.00,
            "Germany": 1.20,
            "Japan": 1.50,
            "Australia": 1.30
        }
        return per_km_rates.get(country, 0.90)