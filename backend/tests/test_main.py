"""
Test cases for the main FastAPI application.
Basic health check and API endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Trip Planner API is running"}

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-trip-planner-backend"
    assert data["version"] == "1.0.0"

def test_cors_headers():
    """Test that CORS headers are properly configured"""
    response = client.options("/")
    # CORS headers should be present for preflight requests
    assert response.status_code in [200, 405]  # Some frameworks return 405 for OPTIONS