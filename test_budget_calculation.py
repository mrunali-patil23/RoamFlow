#!/usr/bin/env python3
"""
Test script to check budget calculation and cost breakdown.
"""

import requests
import json
from datetime import datetime, timedelta

# API configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
TRIP_PLANNING_URL = f"{BASE_URL}/trip-planning/create"

def test_budget_calculation():
    """Test budget calculation and cost breakdown."""
    
    # Login first
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(LOGIN_URL, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
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
        "max_budget_inr": 50000,  # ₹50,000 budget
        "interests": ["nature", "food"]
    }
    
    print("🚀 Creating trip plan...")
    print(f"📍 Destination: {trip_preferences['destination']}")
    print(f"📅 Dates: {trip_preferences['start_date']} to {trip_preferences['end_date']}")
    print(f"💰 Budget: ₹{trip_preferences['max_budget_inr']:,}")
    
    # Create trip plan
    response = requests.post(TRIP_PLANNING_URL, json=trip_preferences, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Trip creation failed: {response.status_code}")
        print(response.text)
        return
    
    trip_plan = response.json()
    print("✅ Trip plan created successfully!")
    
    # Analyze cost breakdown
    print("\n💰 COST BREAKDOWN ANALYSIS:")
    print("=" * 60)
    
    cost_breakdown = trip_plan.get("cost_breakdown", {})
    budget_status = trip_plan.get("budget_status", {})
    itinerary = trip_plan.get("itinerary", {})
    
    print(f"📊 Cost Breakdown (from cost_breakdown):")
    print(f"   ✈️  Flights: ₹{cost_breakdown.get('flight_cost_inr', 0):,.2f}")
    print(f"   🏨 Hotels: ₹{cost_breakdown.get('hotel_cost_inr', 0):,.2f}")
    print(f"   🏛️  Attractions: ₹{cost_breakdown.get('attractions_cost_inr', 0):,.2f}")
    print(f"   🎭 Events: ₹{cost_breakdown.get('events_cost_inr', 0):,.2f}")
    print(f"   🍽️  Local Expenses: ₹{cost_breakdown.get('local_expenses_inr', 0):,.2f}")
    print(f"   💰 TOTAL (Cost Service): ₹{cost_breakdown.get('total_cost_inr', 0):,.2f}")
    
    print(f"\n📊 Itinerary Cost:")
    print(f"   💰 TOTAL (Itinerary): ₹{itinerary.get('total_cost_inr', 0):,.2f}")
    
    print(f"\n📊 Budget Status:")
    print(f"   Status: {budget_status.get('status', 'Unknown')}")
    print(f"   Difference: ₹{budget_status.get('difference_inr', 0):,.2f}")
    print(f"   Budget: ₹{trip_preferences['max_budget_inr']:,}")
    
    if budget_status.get('suggestions'):
        print(f"   Suggestions:")
        for suggestion in budget_status.get('suggestions', []):
            print(f"     • {suggestion}")
    
    # Compare the two totals
    cost_service_total = cost_breakdown.get('total_cost_inr', 0)
    itinerary_total = itinerary.get('total_cost_inr', 0)
    
    print(f"\n🔍 COMPARISON:")
    print(f"   Cost Service Total: ₹{cost_service_total:,.2f}")
    print(f"   Itinerary Total: ₹{itinerary_total:,.2f}")
    print(f"   Difference: ₹{abs(cost_service_total - itinerary_total):,.2f}")
    
    if abs(cost_service_total - itinerary_total) > 100:
        print("   ⚠️  WARNING: Significant difference between cost calculations!")
    else:
        print("   ✅ Cost calculations are consistent")
    
    # Check if budget status makes sense
    budget = trip_preferences['max_budget_inr']
    actual_cost = cost_service_total
    
    print(f"\n🎯 BUDGET ANALYSIS:")
    print(f"   Budget: ₹{budget:,}")
    print(f"   Actual Cost: ₹{actual_cost:,.2f}")
    print(f"   Remaining: ₹{budget - actual_cost:,.2f}")
    
    if actual_cost <= budget:
        expected_status = "Within Budget"
    elif actual_cost <= budget * 1.1:
        expected_status = "Slightly Over Budget"
    else:
        expected_status = "Over Budget"
    
    actual_status = budget_status.get('status', 'Unknown')
    
    print(f"   Expected Status: {expected_status}")
    print(f"   Actual Status: {actual_status}")
    
    if expected_status == actual_status:
        print("   ✅ Budget status is correct!")
    else:
        print("   ❌ Budget status calculation issue!")

if __name__ == "__main__":
    print("🧪 Testing Budget Calculation")
    print("=" * 60)
    
    try:
        test_budget_calculation()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()