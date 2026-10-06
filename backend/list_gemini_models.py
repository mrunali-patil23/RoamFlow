#!/usr/bin/env python3
"""
List available Gemini models.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_models():
    """List available Gemini models"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        print("Available Gemini models:")
        print("=" * 40)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✓ {model.name}")
        
        print("=" * 40)
        
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()