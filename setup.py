#!/usr/bin/env python3
"""
Setup script for AI Travel Planner backend
Run this script to set up the Python virtual environment and install dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {command}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Main setup function"""
    print("Setting up AI Travel Planner backend...")
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("Error: backend directory not found. Please run this from the project root.")
        sys.exit(1)
    
    # Create virtual environment
    print("\n1. Creating Python virtual environment...")
    venv_path = Path("backend/venv")
    if venv_path.exists():
        print("Virtual environment already exists, skipping creation.")
    else:
        result = run_command(f"{sys.executable} -m venv backend/venv")
        if not result:
            print("Failed to create virtual environment")
            sys.exit(1)
    
    # Determine activation script path
    if os.name == 'nt':  # Windows
        activate_script = "backend/venv/Scripts/activate"
        pip_path = "backend/venv/Scripts/pip"
    else:  # Unix/Linux/macOS
        activate_script = "backend/venv/bin/activate"
        pip_path = "backend/venv/bin/pip"
    
    # Install dependencies
    print("\n2. Installing Python dependencies...")
    result = run_command(f"{pip_path} install -r backend/requirements.txt")
    if not result:
        print("Failed to install dependencies")
        sys.exit(1)
    
    print("\n✓ Backend setup complete!")
    print(f"\nTo activate the virtual environment:")
    if os.name == 'nt':
        print(f"  {activate_script}")
    else:
        print(f"  source {activate_script}")
    
    print("\nTo start the backend server:")
    print("  cd backend")
    print("  python -m uvicorn main:app --reload")

if __name__ == "__main__":
    main()