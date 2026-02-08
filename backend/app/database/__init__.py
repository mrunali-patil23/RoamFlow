"""
Database package for the AI Travel Planner.
"""

from .schemas import (
    SUPABASE_SCHEMA,
    MONGODB_TRIP_SCHEMA,
    MONGODB_USER_PREFERENCES_SCHEMA,
    setup_mongodb_collections
)

__all__ = [
    "SUPABASE_SCHEMA",
    "MONGODB_TRIP_SCHEMA", 
    "MONGODB_USER_PREFERENCES_SCHEMA",
    "setup_mongodb_collections"
]