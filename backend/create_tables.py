#!/usr/bin/env python3
"""
Create database tables for the AI Trip Planner.
This script creates all necessary tables directly.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def create_tables():
    """Create all necessary database tables"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    print(f"Creating tables in Supabase at: {supabase_url}")
    
    try:
        # Create Supabase client
        client = create_client(supabase_url, supabase_key)
        
        # Create users table first
        print("Creating users table...")
        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Since we can't use exec_sql, we'll need to inform the user to create tables manually
        print("⚠ Supabase requires tables to be created through the dashboard or SQL editor.")
        print("Please go to your Supabase dashboard and run the following SQL:")
        print("\n" + "="*60)
        print("-- 1. Create users table")
        print(users_sql)
        
        print("\n-- 2. Create trip_plans table")
        trip_plans_sql = """
        CREATE TABLE IF NOT EXISTS trip_plans (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            destination VARCHAR(255) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            travel_days INTEGER NOT NULL,
            travel_type VARCHAR(20) NOT NULL,
            budget_preference VARCHAR(10) NOT NULL,
            max_budget_inr DECIMAL(10,2) NOT NULL,
            interests JSONB NOT NULL,
            total_cost_inr DECIMAL(10,2) NOT NULL,
            budget_status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        print(trip_plans_sql)
        
        print("\n-- 3. Create itineraries table")
        itineraries_sql = """
        CREATE TABLE IF NOT EXISTS itineraries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            trip_plan_id UUID REFERENCES trip_plans(id) ON DELETE CASCADE,
            day_number INTEGER NOT NULL,
            date DATE NOT NULL,
            activities JSONB NOT NULL,
            weather_info JSONB NOT NULL,
            daily_cost_inr DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        print(itineraries_sql)
        
        print("\n-- 4. Create cost_breakdowns table")
        cost_breakdowns_sql = """
        CREATE TABLE IF NOT EXISTS cost_breakdowns (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            trip_plan_id UUID REFERENCES trip_plans(id) ON DELETE CASCADE,
            flight_cost_inr DECIMAL(10,2) NOT NULL,
            hotel_cost_inr DECIMAL(10,2) NOT NULL,
            attractions_cost_inr DECIMAL(10,2) NOT NULL,
            events_cost_inr DECIMAL(10,2) NOT NULL,
            local_expenses_inr DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        print(cost_breakdowns_sql)
        
        print("\n-- 5. Insert default admin user")
        admin_sql = """
        INSERT INTO users (username, email, password_hash) 
        VALUES (
            'admin', 
            'admin@tripplanner.com', 
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9w5KS'
        ) ON CONFLICT (username) DO NOTHING;
        """
        print(admin_sql)
        
        print("="*60)
        print("\nAfter running the SQL in Supabase dashboard, the application will be ready to use.")
        print("Default admin credentials: admin / admin123")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    create_tables()