"""
Configuration settings for the AI Trip Planner backend.
Manages environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Database settings
        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
        
        # External API settings
        self.SERP_API_KEY: str = os.getenv("SERP_API_KEY", "")
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        
        # JWT settings
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        
        # API settings
        self.SERP_API_BASE_URL: str = "https://serpapi.com"
        self.GEMINI_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

# Global settings instance
settings = Settings()