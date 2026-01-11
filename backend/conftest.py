"""
Pytest configuration and fixtures for the AI Travel Planner backend.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
from pathlib import Path

# Set test environment variables
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI application.
    This fixture will be available once main.py is implemented.
    """
    # Import here to avoid circular imports and ensure app is configured for testing
    try:
        from main import app
        with TestClient(app) as test_client:
            yield test_client
    except ImportError:
        # If main.py doesn't exist yet, create a mock client
        pytest.skip("FastAPI app not yet implemented")

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for the FastAPI application.
    """
    try:
        from main import app
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    except ImportError:
        pytest.skip("FastAPI app not yet implemented")

@pytest.fixture
def sample_trip_request():
    """Sample trip request data for testing."""
    return {
        "destination": "Paris",
        "days": 5,
        "budget": "moderate",
        "travelers": "couple"
    }

@pytest.fixture
def sample_trip_response():
    """Sample trip response data for testing."""
    return {
        "trip_id": "test-trip-123",
        "destination": "Paris",
        "total_days": 5,
        "daily_plans": [
            {
                "day_number": 1,
                "activities": [
                    {
                        "name": "Visit Eiffel Tower",
                        "description": "Iconic landmark visit",
                        "duration": 120,
                        "cost": 25.0,
                        "category": "sightseeing"
                    }
                ],
                "transport": [
                    {
                        "type": "metro",
                        "provider": "RATP",
                        "cost": 1.90,
                        "duration": 30,
                        "route": "Line 6 to Bir-Hakeim"
                    }
                ],
                "estimated_cost": 26.90
            }
        ],
        "total_budget": 134.50
    }

# Property-based testing configuration
@pytest.fixture
def hypothesis_settings():
    """Configure Hypothesis for property-based testing."""
    from hypothesis import settings, Verbosity
    return settings(
        max_examples=100,
        verbosity=Verbosity.verbose,
        deadline=None,  # Disable deadline for AI API calls
    )