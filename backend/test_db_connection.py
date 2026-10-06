#!/usr/bin/env python3
"""
Test database connection and check existing tables.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection and check tables"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    print(f"Testing connection to: {supabase_url}")
    
    try:
        # Create Supabase client
        client = create_client(supabase_url, supabase_key)
        
        # Test connection by trying to query users table
        print("Testing users table...")
        try:
            result = client.table("users").select("count", count="exact").execute()
            print(f"✓ Users table exists with {result.count} records")
        except Exception as e:
            print(f"✗ Users table error: {e}")
        
        # Test trip_plans table
        print("Testing trip_plans table...")
        try:
            result = client.table("trip_plans").select("count", count="exact").execute()
            print(f"✓ Trip_plans table exists with {result.count} records")
        except Exception as e:
            print(f"✗ Trip_plans table error: {e}")
        
        # Test itineraries table
        print("Testing itineraries table...")
        try:
            result = client.table("itineraries").select("count", count="exact").execute()
            print(f"✓ Itineraries table exists with {result.count} records")
        except Exception as e:
            print(f"✗ Itineraries table error: {e}")
        
        # Test cost_breakdowns table
        print("Testing cost_breakdowns table...")
        try:
            result = client.table("cost_breakdowns").select("count", count="exact").execute()
            print(f"✓ Cost_breakdowns table exists with {result.count} records")
        except Exception as e:
            print(f"✗ Cost_breakdowns table error: {e}")
        
        print("✓ Database connection test completed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()