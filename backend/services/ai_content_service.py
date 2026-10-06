"""
AI Content Generation Service using Gemini API.

This service provides AI-generated descriptions and travel advice using Google's Gemini API.
It handles attraction descriptions, hotel descriptions, event descriptions, weather-aware
travel tips, and cost-saving advice generation.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class BudgetStatus:
    """Budget status information for cost-saving advice."""
    status: str  # "Within Budget", "Slightly Over Budget", "Over Budget"
    difference_inr: float
    max_budget_inr: float
    total_cost_inr: float


class AIContentService:
    """Service for generating AI content using Gemini API."""
    
    def __init__(self):
        """Initialize the AI content service with Gemini API configuration."""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            # In testing or development mode, we can work without the API key
            # The service will return default responses
            logger.warning("GEMINI_API_KEY environment variable not found. Using fallback mode.")
            self.model = None
            self.generation_config = {}
            return
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generation configuration
        self.generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 150,
            'top_p': 0.8,
            'top_k': 40
        }
    
    def generate_attraction_description(self, attraction: Dict[str, Any]) -> str:
        """
        Generate a 2-3 line description for an attraction.
        
        Args:
            attraction: Dictionary containing attraction data from SERP API
            
        Returns:
            str: Generated description (2-3 lines)
        """
        # Fallback for testing/development mode
        if not self.model:
            name = attraction.get('title', 'this attraction')
            rating = attraction.get('rating', 'N/A')
            return f"{name} is a notable destination with a rating of {rating}. It offers visitors a unique experience and is worth including in your itinerary."
        
        try:
            # Extract relevant information from attraction data
            name = attraction.get('title', 'Unknown Attraction')
            rating = attraction.get('rating', 'N/A')
            address = attraction.get('address', '')
            type_info = attraction.get('type', '')
            
            # Create prompt for attraction description
            prompt = f"""Generate a concise 2-3 line description for this tourist attraction:
            
Name: {name}
Rating: {rating}
Location: {address}
Type: {type_info}

The description should be engaging, informative, and highlight what makes this attraction special. Focus on key features, atmosphere, and visitor experience. Keep it under 150 words."""
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text.strip() if response.text else f"A popular attraction in the area with a rating of {rating}."
            
        except Exception as e:
            logger.error(f"Error generating attraction description: {e}")
            # Fallback description
            name = attraction.get('title', 'this attraction')
            rating = attraction.get('rating', 'N/A')
            return f"{name} is a notable destination with a rating of {rating}. It offers visitors a unique experience and is worth including in your itinerary."
    
    def generate_hotel_description(self, hotel: Dict[str, Any]) -> str:
        """
        Generate a 2-3 line description for a hotel.
        
        Args:
            hotel: Dictionary containing hotel data from SERP API
            
        Returns:
            str: Generated description (2-3 lines)
        """
        # Fallback for testing/development mode
        if not self.model:
            name = hotel.get('name', 'this hotel')
            rating = hotel.get('overall_rating', hotel.get('rating', 'N/A'))
            return f"{name} provides comfortable accommodation with a rating of {rating}. It offers essential amenities and good service for travelers."
        
        try:
            # Extract relevant information from hotel data
            name = hotel.get('name', 'Unknown Hotel')
            rating = hotel.get('overall_rating', hotel.get('rating', 'N/A'))
            price = hotel.get('rate_per_night', {}).get('lowest', 'N/A')
            amenities = hotel.get('amenities', [])
            location = hotel.get('neighborhood', hotel.get('location', ''))
            
            # Create prompt for hotel description
            prompt = f"""Generate a concise 2-3 line description for this hotel:
            
Name: {name}
Rating: {rating}
Price per night: {price}
Location: {location}
Amenities: {', '.join(amenities[:5]) if amenities else 'Standard amenities'}

The description should highlight the hotel's key features, comfort level, and what guests can expect. Focus on location benefits, amenities, and overall experience. Keep it under 150 words."""
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text.strip() if response.text else f"A comfortable hotel with a rating of {rating}, offering good value for money."
            
        except Exception as e:
            logger.error(f"Error generating hotel description: {e}")
            # Fallback description
            name = hotel.get('name', 'this hotel')
            rating = hotel.get('overall_rating', hotel.get('rating', 'N/A'))
            return f"{name} provides comfortable accommodation with a rating of {rating}. It offers essential amenities and good service for travelers."
    
    def generate_event_description(self, event: Dict[str, Any]) -> str:
        """
        Generate a 2-3 line description for an event.
        
        Args:
            event: Dictionary containing event data from SERP API
            
        Returns:
            str: Generated description (2-3 lines)
        """
        # Fallback for testing/development mode
        if not self.model:
            title = event.get('title', 'this event')
            event_type = event.get('event_category', 'event')
            return f"{title} is a {event_type.lower()} that offers visitors a unique cultural experience and entertainment opportunity."
        
        try:
            # Extract relevant information from event data
            title = event.get('title', 'Unknown Event')
            date = event.get('date', {}).get('start_date', 'TBD')
            venue = event.get('venue', {}).get('name', 'Various locations')
            description = event.get('description', '')
            event_type = event.get('event_category', 'Event')
            
            # Create prompt for event description
            prompt = f"""Generate a concise 2-3 line description for this event:
            
Title: {title}
Date: {date}
Venue: {venue}
Type: {event_type}
Details: {description[:200] if description else 'Local event'}

The description should capture the essence of the event, its appeal to visitors, and what attendees can expect. Focus on the experience, atmosphere, and cultural significance. Keep it under 150 words."""
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text.strip() if response.text else f"{title} is an exciting {event_type.lower()} taking place at {venue}."
            
        except Exception as e:
            logger.error(f"Error generating event description: {e}")
            # Fallback description
            title = event.get('title', 'this event')
            event_type = event.get('event_category', 'event')
            return f"{title} is a {event_type.lower()} that offers visitors a unique cultural experience and entertainment opportunity."
    
    def generate_weather_travel_tips(self, weather_data: Dict[str, Any], destination: str) -> str:
        """
        Generate weather-aware travel tips based on weather conditions.
        
        Args:
            weather_data: Dictionary containing weather information
            destination: Destination name
            
        Returns:
            str: Generated travel tips based on weather
        """
        try:
            # Extract weather information
            current_temp = weather_data.get('temperature', 'N/A')
            condition = weather_data.get('weather', weather_data.get('condition', 'Unknown'))
            humidity = weather_data.get('humidity', 'N/A')
            precipitation = weather_data.get('precipitation', weather_data.get('rain', 0))
            
            # Create prompt for weather-aware travel tips
            prompt = f"""Generate practical travel tips for visiting {destination} based on these weather conditions:
            
Temperature: {current_temp}
Weather Condition: {condition}
Humidity: {humidity}
Precipitation: {precipitation}

Provide 3-4 specific, actionable tips about:
- What to wear/pack
- Best times for outdoor activities
- Indoor alternatives if needed
- Health and comfort considerations

Keep the advice practical and concise."""
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text.strip() if response.text else f"Check the weather forecast for {destination} and pack accordingly. Consider bringing layers and rain protection."
            
        except Exception as e:
            logger.error(f"Error generating weather travel tips: {e}")
            # Fallback tips
            return f"Check the current weather conditions in {destination} before heading out. Pack appropriate clothing and consider indoor alternatives for extreme weather."
    
    def generate_cost_saving_advice(self, budget_status: BudgetStatus, trip_components: Optional[Dict[str, float]] = None) -> List[str]:
        """
        Generate cost-saving advice when budget is exceeded.
        
        Args:
            budget_status: Budget status information
            trip_components: Optional breakdown of trip costs by component
            
        Returns:
            List[str]: List of cost-saving suggestions
        """
        try:
            # Prepare cost breakdown information
            cost_breakdown = ""
            if trip_components:
                cost_breakdown = "\n".join([f"{component}: ₹{cost:,.2f}" for component, cost in trip_components.items()])
            
            # Create prompt for cost-saving advice
            prompt = f"""Generate specific cost-saving advice for a trip that is over budget:
            
Budget Status: {budget_status.status}
Maximum Budget: ₹{budget_status.max_budget_inr:,.2f}
Total Cost: ₹{budget_status.total_cost_inr:,.2f}
Over Budget By: ₹{budget_status.difference_inr:,.2f}

{f'Cost Breakdown:{cost_breakdown}' if cost_breakdown else ''}

Provide 4-5 specific, actionable cost-saving suggestions that could help reduce the trip cost. Focus on:
- Alternative accommodation options
- Transportation savings
- Activity alternatives
- Timing considerations
- Local vs tourist pricing

Make each suggestion practical and specific."""
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            if response.text:
                # Split response into individual suggestions
                suggestions = [line.strip() for line in response.text.strip().split('\n') if line.strip() and not line.strip().startswith('#')]
                # Clean up bullet points and numbering
                cleaned_suggestions = []
                for suggestion in suggestions:
                    cleaned = suggestion.lstrip('•-*1234567890. ').strip()
                    if cleaned and len(cleaned) > 10:  # Filter out very short lines
                        cleaned_suggestions.append(cleaned)
                return cleaned_suggestions[:5]  # Return max 5 suggestions
            
            # Fallback suggestions
            return [
                "Consider staying in budget accommodations or hostels instead of luxury hotels",
                "Book flights in advance or look for alternative travel dates with lower prices",
                "Choose free or low-cost attractions and activities over expensive tourist experiences",
                "Eat at local restaurants instead of tourist-oriented establishments",
                "Use public transportation instead of taxis or private transfers"
            ]
            
        except Exception as e:
            logger.error(f"Error generating cost-saving advice: {e}")
            # Fallback advice
            return [
                "Look for budget accommodation options to reduce lodging costs",
                "Consider alternative travel dates for better flight prices",
                "Explore free attractions and activities in the destination",
                "Choose local dining options over expensive tourist restaurants",
                "Use public transportation to save on travel costs"
            ]
    
    def validate_api_connection(self) -> bool:
        """
        Validate that the Gemini API connection is working.
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            # Simple test generation
            response = self.model.generate_content(
                "Generate a single word: 'test'",
                generation_config={'max_output_tokens': 10}
            )
            return bool(response.text and 'test' in response.text.lower())
        except Exception as e:
            logger.error(f"API connection validation failed: {e}")
            return False