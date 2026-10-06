#!/usr/bin/env python3
"""
Test script to check what data is being returned from SERP API.
"""

import sys
import os
sys.path.append('backend')

from services.data_integration_service import DataIntegrationService
from models.travel_data import DateRange
from models.trip_preferences import BudgetLevel
from datetime import datetime, timedelta

def test_serp_data():
    """Test what data is being returned from SERP API."""
    
    service = DataIntegrationService()
    
    # Test parameters
    destination = "Goa"
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(days=3)
    date_range = DateRange(start_date.date(), end_date.date())
    budget = BudgetLevel.MEDIUM
    interests = ["nature", "food"]
    
    print("🧪 Testing SERP API Data Retrieval")
    print("=" * 50)
    print(f"📍 Destination: {destination}")
    print(f"📅 Dates: {date_range.start_date} to {date_range.end_date}")
    print(f"💰 Budget: {budget}")
    print(f"🎯 Interests: {interests}")
    print()
    
    # Test flights
    print("✈️  Testing Flight Data...")
    try:
        flight_data = service.fetch_flights(destination, date_range)
        print(f"   Flights found: {len(flight_data.flights)}")
        if flight_data.flights:
            print(f"   First flight: {flight_data.flights[0]}")
        else:
            print("   No flight data returned")
    except Exception as e:
        print(f"   Error fetching flights: {e}")
    
    print()
    
    # Test hotels
    print("🏨 Testing Hotel Data...")
    try:
        hotel_data = service.fetch_hotels(destination, budget, date_range)
        print(f"   Hotels found: {len(hotel_data.hotels)}")
        if hotel_data.hotels:
            print(f"   First hotel: {hotel_data.hotels[0]}")
        else:
            print("   No hotel data returned")
    except Exception as e:
        print(f"   Error fetching hotels: {e}")
    
    print()
    
    # Test attractions
    print("🏛️  Testing Attraction Data...")
    try:
        attraction_data = service.fetch_attractions(destination, interests)
        print(f"   Attractions found: {len(attraction_data.attractions)}")
        if attraction_data.attractions:
            print(f"   First attraction: {attraction_data.attractions[0]}")
    except Exception as e:
        print(f"   Error fetching attractions: {e}")
    
    print()
    
    # Test events
    print("🎭 Testing Event Data...")
    try:
        event_data = service.fetch_events(destination, date_range)
        print(f"   Events found: {len(event_data.events)}")
        if event_data.events:
            print(f"   First event: {event_data.events[0]}")
    except Exception as e:
        print(f"   Error fetching events: {e}")

if __name__ == "__main__":
    test_serp_data()