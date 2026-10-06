#!/usr/bin/env python3
"""
Test script to verify budget status calculation with different budgets.
"""

import requests
import json
from datetime import datetime, timedelta

# API configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
TRIP_PLANNING_URL = f"{BASE_URL}/trip-planning/create"

def test_budget_status(budget_amount, expected_status):
    """Test budget status with a specific budget amount."""
    
    # Login first
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(LOGIN_URL, json=login_data)
    if login_response.status_code != 200:
        return False
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
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
        "max_budget_inr": budget_amount,
        "interests": ["nature", "food"]
    }
    
    # Create trip plan
    response = requests.post(TRIP_PLANNING_URL, json=trip_preferences, headers=headers)
    
    if response.status_code != 200:
        return False
    
    trip_plan = response.json()
    budget_status = trip_plan.get("budget_status", {})
    actual_status = budget_status.get("status", "Unknown")
    total_cost = trip_plan.get("cost_breakdown", {}).get("total_cost_inr", 0)
    
    print(f"💰 Budget: ₹{budget_amount:,}")
    print(f"💸 Total Cost: ₹{total_cost:,.2f}")
    print(f"📊 Expected Status: {expected_status}")
    print(f"📊 Actual Status: {actual_status}")
    
    success = actual_status == expected_status
    print(f"{'✅' if success else '❌'} {'PASS' if success else 'FAIL'}")
    print()
    
    return success

def main():
    print("🧪 Testing Budget Status Calculation")
    print("=" * 50)
    
    # Test different budget scenarios
    test_cases = [
        (50000, "Within Budget"),      # ₹50,000 - should be within budget
        (25000, "Within Budget"),      # ₹25,000 - should be within budget (close)
        (20000, "Slightly Over Budget"), # ₹20,000 - should be slightly over
        (10000, "Over Budget"),        # ₹10,000 - should be over budget
    ]
    
    passed = 0
    total = len(test_cases)
    
    for budget, expected in test_cases:
        if test_budget_status(budget, expected):
            passed += 1
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All budget status tests passed!")
    else:
        print("⚠️  Some budget status tests failed")

if __name__ == "__main__":
    main()