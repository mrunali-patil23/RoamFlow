#!/usr/bin/env python3
"""
Detailed debug script for attractions cost calculation.
"""

import sys
import os
sys.path.append('backend')

from services.data_integration_service import DataIntegrationService
from services.cost_calculation_service import CostCalculationService
from models.travel_data import DateRange
from models.trip_preferences import BudgetLevel
from datetime import datetime, timedelta

def debug_attractions_detailed():
    """Debug attractions cost calculation in detail."""
    
    data_service = DataIntegrationService()
    cost_service = CostCalculationService()
    
    # Test parameters
    destination = "Goa"
    interests = ["nature", "food"]
    
    print("🧪 Detailed Attractions Cost Debug")
    print("=" * 60)
    
    # Fetch attraction data
    attraction_data = data_service.fetch_attractions(destination, interests)
    print(f"Attractions found: {len(attraction_data.attractions)}")
    
    # Step through the cost calculation logic
    total_cost = 0.0
    print(f"\n💰 Processing each attraction:")
    
    for i, attraction in enumerate(attraction_data.attractions):
        print(f"\n--- Attraction {i+1}: {attraction.get('title', 'Unknown')} ---")
        
        # Check price_inr field
        price_inr = attraction.get('price_inr')
        print(f"   price_inr field: {price_inr}")
        
        # Check price field
        price_field = attraction.get('price')
        print(f"   price field: {price_field} (type: {type(price_field)})")
        
        # Follow the same logic as the cost service
        if 'price_inr' in attraction:
            price = attraction['price_inr']
            print(f"   Using price_inr: {price}")
        else:
            # Extract entry fee if available from other fields
            price_info = attraction.get('price', {})
            if isinstance(price_info, dict):
                price = price_info.get('value', 0)
                print(f"   Using price.value: {price}")
            elif price_info:
                price = price_info
                print(f"   Using price directly: {price}")
            else:
                # Estimate based on attraction type
                price = cost_service._estimate_attraction_cost(attraction)
                print(f"   Using estimate: {price}")
        
        # Convert to float and add to total
        try:
            price_float = float(price) if price else 0.0
            total_cost += price_float
            print(f"   Final price: ₹{price_float:.2f}")
        except (ValueError, TypeError) as e:
            # If price is not a number, use estimate
            estimate = cost_service._estimate_attraction_cost(attraction)
            total_cost += estimate
            print(f"   Error converting price ({e}), using estimate: ₹{estimate:.2f}")
        
        print(f"   Running total: ₹{total_cost:.2f}")
        
        # Stop after first 5 for readability
        if i >= 4:
            print(f"\n... (showing first 5 of {len(attraction_data.attractions)} attractions)")
            break
    
    # Calculate the rest without detailed output
    for attraction in attraction_data.attractions[5:]:
        if 'price_inr' in attraction:
            price = attraction['price_inr']
        else:
            price_info = attraction.get('price', {})
            if isinstance(price_info, dict):
                price = price_info.get('value', 0)
            elif price_info:
                price = price_info
            else:
                price = cost_service._estimate_attraction_cost(attraction)
        
        try:
            price_float = float(price) if price else 0.0
            total_cost += price_float
        except (ValueError, TypeError):
            total_cost += cost_service._estimate_attraction_cost(attraction)
    
    print(f"\n📊 Final Results:")
    print(f"   Manual calculation total: ₹{total_cost:.2f}")
    
    # Compare with cost service method
    service_total = cost_service._calculate_attractions_costs(attraction_data)
    print(f"   Cost service total: ₹{service_total:.2f}")
    
    if abs(total_cost - service_total) < 0.01:
        print("✅ Calculations match!")
    else:
        print(f"❌ Calculations differ by ₹{abs(total_cost - service_total):.2f}")

if __name__ == "__main__":
    debug_attractions_detailed()