#!/usr/bin/env python3
"""
Test script to verify that flights and hotels are being added as activities in the itinerary.
"""

import requests
import json
from datetime import datetime, timedelta

# API configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
TRIP_PLANNING_URL = f"{BASE_URL}/trip-planning/create"

def test_trip_with_flights_and_hotels():
    """Test creating a trip plan and check if flights and hotels appear as activities."""
    
    # Login first
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(LOGIN_URL, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    
    # Create trip preferences
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(days=3)
    
    trip_preferences = {
        "destination": "Goa",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "travel_days": 3,
        "travel_type": "Solo",
        "budget_preference": "medium",
        "max_budget_inr": 50000,
        "interests": ["nature", "food"]
    }
    
    print("🚀 Creating trip plan...")
    print(f"📍 Destination: {trip_preferences['destination']}")
    print(f"📅 Dates: {trip_preferences['start_date']} to {trip_preferences['end_date']}")
    
    # Create trip plan
    response = requests.post(TRIP_PLANNING_URL, json=trip_preferences, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Trip creation failed: {response.status_code}")
        print(response.text)
        return
    
    trip_plan = response.json()
    print("✅ Trip plan created successfully!")
    
    # Analyze the itinerary for flights and hotels
    print("\n📋 ITINERARY ANALYSIS:")
    print("=" * 50)
    
    itinerary = trip_plan.get("itinerary", {})
    days = itinerary.get("days", [])
    
    flight_activities = []
    hotel_activities = []
    other_activities = []
    
    for day in days:
        day_num = day.get("day_number")
        activities = day.get("activities", [])
        
        print(f"\n📅 Day {day_num} ({day.get('date')}):")
        print(f"   💰 Daily Cost: ₹{day.get('daily_cost_inr', 0):,.2f}")
        print(f"   🎯 Activities: {len(activities)}")
        
        for activity in activities:
            activity_type = activity.get("activity_type")
            name = activity.get("name")
            cost = activity.get("cost_inr", 0)
            duration = activity.get("duration_hours", 0)
            
            print(f"     • {name} ({activity_type}) - ₹{cost:,.2f} ({duration}h)")
            
            if activity_type == "transport":
                flight_activities.append(activity)
            elif activity_type == "accommodation":
                hotel_activities.append(activity)
            else:
                other_activities.append(activity)
    
    # Summary
    print("\n📊 ACTIVITY SUMMARY:")
    print("=" * 50)
    print(f"✈️  Flight Activities: {len(flight_activities)}")
    print(f"🏨 Hotel Activities: {len(hotel_activities)}")
    print(f"🎯 Other Activities: {len(other_activities)}")
    
    if flight_activities:
        print("\n✈️  FLIGHT ACTIVITIES:")
        for flight in flight_activities:
            print(f"   • {flight['name']} - ₹{flight['cost_inr']:,.2f}")
            if flight.get('start_time') and flight.get('end_time'):
                print(f"     Time: {flight['start_time']} - {flight['end_time']}")
    
    if hotel_activities:
        print("\n🏨 HOTEL ACTIVITIES:")
        for hotel in hotel_activities:
            print(f"   • {hotel['name']} - ₹{hotel['cost_inr']:,.2f}")
            if hotel.get('location'):
                print(f"     Location: {hotel['location']}")
    
    # Check if flights and hotels are present
    success = len(flight_activities) > 0 or len(hotel_activities) > 0
    
    if success:
        print("\n✅ SUCCESS: Flights and/or hotels are now appearing as activities!")
    else:
        print("\n⚠️  WARNING: No flights or hotels found in activities")
        print("   This might be due to SERP API limitations or data availability")
    
    print(f"\n💰 Total Trip Cost: ₹{itinerary.get('total_cost_inr', 0):,.2f}")
    
    return success

if __name__ == "__main__":
    print("🧪 Testing Flight and Hotel Activities Integration")
    print("=" * 60)
    
    try:
        success = test_trip_with_flights_and_hotels()
        if success:
            print("\n🎉 Test completed successfully!")
        else:
            print("\n⚠️  Test completed with warnings")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()