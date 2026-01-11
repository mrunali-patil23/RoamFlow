"""
Database schema definitions for the AI Travel Planner.

This module contains SQL schema definitions for Supabase and MongoDB collection schemas.
"""

# Supabase SQL Schema
SUPABASE_SCHEMA = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trips table
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    destination TEXT NOT NULL,
    total_days INTEGER NOT NULL CHECK (total_days > 0 AND total_days <= 30),
    budget_category TEXT CHECK (budget_category IN ('cheap', 'moderate', 'luxury')),
    traveler_type TEXT CHECK (traveler_type IN ('just-me', 'couple', 'family', 'friends')),
    itinerary JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    preferred_budget TEXT CHECK (preferred_budget IN ('cheap', 'moderate', 'luxury')),
    preferred_traveler_type TEXT CHECK (preferred_traveler_type IN ('just-me', 'couple', 'family', 'friends')),
    favorite_destinations TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_trips_destination ON trips(destination);
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Row Level Security (RLS) policies
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Policies for trips table
CREATE POLICY IF NOT EXISTS "Users can view their own trips" ON trips
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert their own trips" ON trips
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can update their own trips" ON trips
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can delete their own trips" ON trips
    FOR DELETE USING (auth.uid() = user_id);

-- Policies for user_preferences table
CREATE POLICY IF NOT EXISTS "Users can view their own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert their own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can update their own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER IF NOT EXISTS update_trips_updated_at 
    BEFORE UPDATE ON trips 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""

# MongoDB Schema Validation
MONGODB_TRIP_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["trip_id", "destination", "total_days", "daily_plans", "total_budget"],
        "properties": {
            "trip_id": {
                "bsonType": "string",
                "description": "Unique trip identifier"
            },
            "destination": {
                "bsonType": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "Travel destination"
            },
            "total_days": {
                "bsonType": "int",
                "minimum": 1,
                "maximum": 30,
                "description": "Total number of days"
            },
            "daily_plans": {
                "bsonType": "array",
                "minItems": 1,
                "items": {
                    "bsonType": "object",
                    "required": ["day_number", "activities", "estimated_cost"],
                    "properties": {
                        "day_number": {
                            "bsonType": "int",
                            "minimum": 1
                        },
                        "activities": {
                            "bsonType": "array",
                            "minItems": 1,
                            "items": {
                                "bsonType": "object",
                                "required": ["name", "description", "duration", "cost", "category"],
                                "properties": {
                                    "name": {"bsonType": "string", "minLength": 1},
                                    "description": {"bsonType": "string", "minLength": 1},
                                    "duration": {"bsonType": "int", "minimum": 30},
                                    "cost": {"bsonType": "double", "minimum": 0},
                                    "category": {
                                        "enum": ["sightseeing", "dining", "entertainment", "cultural"]
                                    }
                                }
                            }
                        },
                        "transport": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["type", "provider", "cost", "duration", "route"],
                                "properties": {
                                    "type": {
                                        "enum": ["flight", "taxi", "bus", "metro", "walking"]
                                    },
                                    "provider": {"bsonType": "string", "minLength": 1},
                                    "cost": {"bsonType": "double", "minimum": 0},
                                    "duration": {"bsonType": "int", "minimum": 1},
                                    "route": {"bsonType": "string", "minLength": 1}
                                }
                            }
                        },
                        "estimated_cost": {
                            "bsonType": "double",
                            "minimum": 0
                        }
                    }
                }
            },
            "total_budget": {
                "bsonType": "double",
                "minimum": 0,
                "description": "Total estimated budget"
            },
            "created_at": {
                "bsonType": "date",
                "description": "Creation timestamp"
            },
            "updated_at": {
                "bsonType": "date",
                "description": "Last update timestamp"
            }
        }
    }
}

MONGODB_USER_PREFERENCES_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["user_id"],
        "properties": {
            "user_id": {
                "bsonType": "string",
                "description": "Unique user identifier"
            },
            "preferred_budget": {
                "enum": ["cheap", "moderate", "luxury"],
                "description": "User's preferred budget category"
            },
            "preferred_traveler_type": {
                "enum": ["just-me", "couple", "family", "friends"],
                "description": "User's preferred traveler type"
            },
            "favorite_destinations": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string"
                },
                "description": "List of user's favorite destinations"
            },
            "created_at": {
                "bsonType": "date",
                "description": "Creation timestamp"
            },
            "updated_at": {
                "bsonType": "date",
                "description": "Last update timestamp"
            }
        }
    }
}


def setup_mongodb_collections(db):
    """
    Set up MongoDB collections with validation schemas and indexes.
    
    Args:
        db: MongoDB database instance
    """
    # Create trips collection with validation
    try:
        db.create_collection("trips", validator=MONGODB_TRIP_SCHEMA)
    except Exception:
        # Collection might already exist, update validator
        db.command("collMod", "trips", validator=MONGODB_TRIP_SCHEMA)
    
    # Create user_preferences collection with validation
    try:
        db.create_collection("user_preferences", validator=MONGODB_USER_PREFERENCES_SCHEMA)
    except Exception:
        # Collection might already exist, update validator
        db.command("collMod", "user_preferences", validator=MONGODB_USER_PREFERENCES_SCHEMA)
    
    # Create indexes for better performance
    trips_collection = db.trips
    preferences_collection = db.user_preferences
    
    # Trips collection indexes
    trips_collection.create_index("user_id")
    trips_collection.create_index("destination")
    trips_collection.create_index("created_at")
    trips_collection.create_index([("destination", 1), ("created_at", -1)])
    
    # User preferences collection indexes
    preferences_collection.create_index("user_id", unique=True)