"""
AI Trip Planner Backend - FastAPI Application
Main entry point for the backend API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import auth, trip_preferences, trip_planning
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Trip Planner API",
    description="Backend API for AI-powered Real-Time Trip Planner",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Vite dev server and alternative ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(trip_preferences.router)
app.include_router(trip_planning.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Trip Planner API is running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "ai-trip-planner-backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)