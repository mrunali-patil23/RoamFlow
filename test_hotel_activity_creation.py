#!/usr/bin/env python3
"""
Test script to specifically test hotel activity creation.
"""

import sys
import os
sys.path.append('backend')

from models.itinerary_models import Activity
from services.data_integration_service import DataIntegrationService
from models.travel_data import DateRange
from models.trip_preferences import BudgetLevel
from datetime import datetime, timedelta

def test_hotel_activity_creation():
    """Test creating hotel activities from real SERP data."""
    
    service = DataIntegrationService()
    
    # Test parameters
    destination = "Goa"
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(days=3)
    date_range = DateRange(start_date.date(), end_date.date())
    budget = BudgetLevel.MEDIUM
    
    print("🧪 Testing Hotel Activity Creation")
    print("=" * 50)
    
    # Fetch hotel data
    print("🏨 Fetching hotel data...")
    hotel_data = service.fetch_hotels(destination, budget, date_range)
    print(f"   Hotels found: {len(hotel_data.hotels)}")
    
    if not hotel_data.hotels:
        print("❌ No hotel data available for testing")
        return
    
    # Test creating activities from hotel data
    print("\n🔧 Creating hotel activities...")
    hotel_activities = []
    
    for i, hotel in enumerate(hotel_data.hotels[:3]):  # Test first 3 hotels
        print(f"\n   Hotel {i+1}: {hotel.get('name', 'Unknown')}")
        print(f"   Raw data keys: {list(hotel.keys())}")
        
        try:
            activity = Activity.from_hotel_data(hotel)
            hotel_activities.append(activity)
            
            print(f"   ✅ Activity created:")
            print(f"      Name: {activity.name}")
            print(f"      Type: {activity.activity_type}")
            print(f"      Cost: ₹{activity.cost_inr:,.2f}")
            print(f"      Duration: {activity.duration_hours}h")
            print(f"      Location: {activity.location}")
            print(f"      Rating: {activity.rating}")
            print(f"      Booking Required: {activity.booking_required}")
            
        except Exception as e:
            print(f"   ❌ Error creating activity: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 Summary: Created {len(hotel_activities)} hotel activities")
    
    return len(hotel_activities) > 0

if __name__ == "__main__":
    test_hotel_activity_creation()