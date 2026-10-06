#!/usr/bin/env python3
"""
Debug script to check attractions cost calculation.
"""

import sys
import os
sys.path.append('backend')

from services.data_integration_service import DataIntegrationService
from services.cost_calculation_service import CostCalculationService
from models.travel_data import DateRange
from models.trip_preferences import BudgetLevel
from datetime import datetime, timedelta

def debug_attractions_cost():
    """Debug attractions cost calculation."""
    
    data_service = DataIntegrationService()
    cost_service = CostCalculationService()
    
    # Test parameters
    destination = "Goa"
    interests = ["nature", "food"]
    
    print("🧪 Debugging Attractions Cost Calculation")
    print("=" * 60)
    
    # Fetch attraction data
    print("🏛️  Fetching attraction data...")
    attraction_data = data_service.fetch_attractions(destination, interests)
    print(f"   Attractions found: {len(attraction_data.attractions)}")
    
    if not attraction_data.attractions:
        print("❌ No attraction data available")
        return
    
    # Show first few attractions
    print(f"\n📋 First 5 attractions:")
    for i, attraction in enumerate(attraction_data.attractions[:5]):
        print(f"   {i+1}. {attraction.get('title', 'Unknown')}")
        print(f"      Price field: {attraction.get('price', 'None')}")
        print(f"      Price INR field: {attraction.get('price_inr', 'None')}")
        print(f"      Rating: {attraction.get('rating', 'None')}")
        print()
    
    # Calculate cost using cost service
    print("💰 Calculating attractions cost...")
    total_cost = cost_service._calculate_attractions_costs(attraction_data)
    print(f"   Total attractions cost: ₹{total_cost:,.2f}")
    
    # Manual calculation for comparison
    print("\n🔍 Manual calculation:")
    manual_total = 0
    for i, attraction in enumerate(attraction_data.attractions):
        # Check different price fields
        price_inr = attraction.get('price_inr', 0)
        price = attraction.get('price', 0)
        
        if price_inr:
            cost = float(price_inr)
        elif price:
            cost = float(price) if isinstance(price, (int, float)) else 0
        else:
            # Use estimate
            cost = cost_service._estimate_attraction_cost(attraction)
        
        manual_total += cost
        
        if i < 5:  # Show first 5
            print(f"   {i+1}. {attraction.get('title', 'Unknown')[:30]}: ₹{cost:.2f}")
    
    print(f"   Manual total: ₹{manual_total:,.2f}")
    
    # Compare
    if abs(total_cost - manual_total) < 0.01:
        print("✅ Cost calculations match!")
    else:
        print(f"❌ Cost calculations differ by ₹{abs(total_cost - manual_total):,.2f}")

if __name__ == "__main__":
    debug_attractions_cost()