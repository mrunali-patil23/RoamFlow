#!/usr/bin/env python3
"""
Test API connections without exposing secrets.
"""

import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_supabase():
    """Test Supabase connection"""
    print("Testing Supabase connection...")
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        client = create_client(supabase_url, supabase_key)
        
        # Try a simple operation (this will fail if tables don't exist, but connection will work)
        try:
            result = client.table("users").select("count", count="exact").execute()
            print("✓ Supabase connection successful - tables exist")
            return True
        except Exception as table_error:
            if "Could not find the table" in str(table_error):
                print("✓ Supabase connection successful - tables need to be created")
                return True
            else:
                print(f"✗ Supabase table error: {table_error}")
                return False
                
    except Exception as e:
        print(f"✗ Supabase connection failed: {e}")
        return False

def test_serp_api():
    """Test SERP API connection"""
    print("Testing SERP API connection...")
    try:
        api_key = os.getenv("SERP_API_KEY")
        
        # Test with a simple search
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": "test",
            "api_key": api_key,
            "num": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "search_metadata" in data:
                print("✓ SERP API connection successful")
                return True
            else:
                print(f"✗ SERP API unexpected response format")
                return False
        else:
            print(f"✗ SERP API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ SERP API connection failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API connection"""
    print("Testing Gemini API connection...")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Test with a simple generation using an available model
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say hello")
        
        if response and response.text:
            print("✓ Gemini API connection successful")
            return True
        else:
            print("✗ Gemini API no response received")
            return False
            
    except Exception as e:
        print(f"✗ Gemini API connection failed: {e}")
        return False

def main():
    """Test all API connections"""
    print("Testing API connections...")
    print("=" * 50)
    
    results = []
    
    # Test each API
    results.append(("Supabase", test_supabase()))
    results.append(("SERP API", test_serp_api()))
    results.append(("Gemini API", test_gemini_api()))
    
    print("\n" + "=" * 50)
    print("API Connection Test Results:")
    
    all_success = True
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{name}: {status}")
        if not success:
            all_success = False
    
    print("=" * 50)
    
    if all_success:
        print("✓ All API connections successful!")
    else:
        print("✗ Some API connections failed!")
    
    return all_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)