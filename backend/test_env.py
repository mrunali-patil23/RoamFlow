#!/usr/bin/env python3
"""
Test environment variables loading.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_vars():
    """Test that all required environment variables are loaded"""
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY", 
        "SERP_API_KEY",
        "GEMINI_API_KEY",
        "SECRET_KEY"
    ]
    
    print("Testing environment variables...")
    print("=" * 50)
    
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Don't print full values for security
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✓ {var}: {masked_value}")
        else:
            print(f"✗ {var}: NOT SET")
            all_present = False
    
    print("=" * 50)
    
    if all_present:
        print("✓ All environment variables are properly loaded!")
        
        # Test API key formats
        print("\nTesting API key formats...")
        
        supabase_url = os.getenv("SUPABASE_URL")
        if supabase_url and supabase_url.startswith("https://") and ".supabase.co" in supabase_url:
            print("✓ SUPABASE_URL format looks correct")
        else:
            print("✗ SUPABASE_URL format may be incorrect")
        
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_key and supabase_key.startswith("eyJ"):
            print("✓ SUPABASE_KEY format looks correct (JWT)")
        else:
            print("✗ SUPABASE_KEY format may be incorrect")
        
        serp_key = os.getenv("SERP_API_KEY")
        if serp_key and len(serp_key) > 30:
            print("✓ SERP_API_KEY format looks correct")
        else:
            print("✗ SERP_API_KEY format may be incorrect")
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key.startswith("AIza"):
            print("✓ GEMINI_API_KEY format looks correct")
        else:
            print("✗ GEMINI_API_KEY format may be incorrect")
        
        return True
    else:
        print("✗ Some environment variables are missing!")
        return False

if __name__ == "__main__":
    success = test_env_vars()
    exit(0 if success else 1)