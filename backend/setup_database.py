#!/usr/bin/env python3
"""
Database setup script for the AI Travel Planner.

This script initializes the database schema for either Supabase or MongoDB
based on the environment configuration.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from app.database.schemas import SUPABASE_SCHEMA, setup_mongodb_collections

# Load environment variables
load_dotenv()


def setup_supabase():
    """Set up Supabase database schema."""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL and SUPABASE_KEY environment variables are required")
            return False
        
        print("🔗 Connecting to Supabase...")
        client = create_client(supabase_url, supabase_key)
        
        print("📋 Creating database schema...")
        # Execute the schema SQL
        # Note: Supabase client doesn't have direct SQL execution in Python
        # This would typically be done through the Supabase dashboard or CLI
        print("⚠️  Please execute the following SQL in your Supabase dashboard:")
        print("=" * 60)
        print(SUPABASE_SCHEMA)
        print("=" * 60)
        
        print("✅ Supabase schema instructions provided")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Supabase: {e}")
        return False


def setup_mongodb():
    """Set up MongoDB database schema."""
    try:
        from pymongo import MongoClient
        
        mongodb_url = os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            print("❌ MONGODB_URL environment variable is required")
            return False
        
        print("🔗 Connecting to MongoDB...")
        client = MongoClient(mongodb_url)
        db = client.travel_planner
        
        print("📋 Setting up collections and schemas...")
        setup_mongodb_collections(db)
        
        print("✅ MongoDB schema setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 AI Travel Planner Database Setup")
    print("=" * 40)
    
    # Determine which database to set up
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        print("📊 Detected Supabase configuration")
        success = setup_supabase()
    elif os.getenv("MONGODB_URL"):
        print("📊 Detected MongoDB configuration")
        success = setup_mongodb()
    else:
        print("❌ No database configuration found!")
        print("Please set either:")
        print("  - SUPABASE_URL and SUPABASE_KEY for Supabase")
        print("  - MONGODB_URL for MongoDB")
        return False
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        return True
    else:
        print("\n💥 Database setup failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)