#!/usr/bin/env python3
"""
Test script to verify that all testing frameworks are properly configured.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_frontend():
    """Test frontend testing setup."""
    print("🧪 Testing frontend setup...")
    
    # Check if frontend directory exists
    if not Path("frontend").exists():
        print("❌ Frontend directory not found")
        return False
    
    # Run frontend tests
    success, stdout, stderr = run_command("npm test -- --passWithNoTests", cwd="frontend")
    
    if success:
        print("✅ Frontend tests configured and working")
        return True
    else:
        print("❌ Frontend tests failed")
        print(f"Error: {stderr}")
        return False

def test_backend():
    """Test backend testing setup."""
    print("🧪 Testing backend setup...")
    
    # Check if backend directory exists
    if not Path("backend").exists():
        print("❌ Backend directory not found")
        return False
    
    # Check if virtual environment exists
    venv_path = Path("backend/venv")
    if not venv_path.exists():
        print("❌ Backend virtual environment not found")
        return False
    
    # Activate virtual environment and run tests
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python.exe"
    else:  # Unix-like
        python_cmd = "venv/bin/python"
    
    success, stdout, stderr = run_command(f"{python_cmd} -m pytest tests/test_example.py -v", cwd="backend")
    
    if success:
        print("✅ Backend tests configured and working")
        return True
    else:
        print("❌ Backend tests failed")
        print(f"Error: {stderr}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing AI Travel Planner testing framework setup...\n")
    
    frontend_ok = test_frontend()
    print()
    backend_ok = test_backend()
    
    print("\n" + "="*50)
    
    if frontend_ok and backend_ok:
        print("✅ All testing frameworks are properly configured!")
        print("\nFrameworks configured:")
        print("  • Frontend: Jest + React Testing Library + fast-check")
        print("  • Backend: pytest + FastAPI TestClient + Hypothesis")
        print("\nYou can now run tests with:")
        print("  • Frontend: cd frontend && npm test")
        print("  • Backend: cd backend && venv\\Scripts\\activate && python -m pytest")
        return True
    else:
        print("❌ Some testing frameworks have issues")
        if not frontend_ok:
            print("  • Frontend testing needs attention")
        if not backend_ok:
            print("  • Backend testing needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)