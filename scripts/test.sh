#!/bin/bash

# Test script for AI Trip Planner
# Runs all tests for both frontend and backend

echo "🧪 Running AI Trip Planner Test Suite"

# Function to run backend tests
run_backend_tests() {
    echo "🐍 Running Python backend tests..."
    cd backend
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run tests with coverage
    echo "📊 Running pytest with coverage..."
    pytest --cov=. --cov-report=term-missing
    BACKEND_EXIT_CODE=$?
    
    cd ..
    return $BACKEND_EXIT_CODE
}

# Function to run frontend tests
run_frontend_tests() {
    echo "⚛️  Running React frontend tests..."
    cd frontend
    
    # Run tests
    echo "🔍 Running vitest..."
    npm test
    FRONTEND_EXIT_CODE=$?
    
    cd ..
    return $FRONTEND_EXIT_CODE
}

# Run tests
run_backend_tests
BACKEND_RESULT=$?

run_frontend_tests
FRONTEND_RESULT=$?

# Report results
echo ""
echo "📋 Test Results:"
if [ $BACKEND_RESULT -eq 0 ]; then
    echo "✅ Backend tests: PASSED"
else
    echo "❌ Backend tests: FAILED"
fi

if [ $FRONTEND_RESULT -eq 0 ]; then
    echo "✅ Frontend tests: PASSED"
else
    echo "❌ Frontend tests: FAILED"
fi

# Exit with error if any tests failed
if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ]; then
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
else
    echo ""
    echo "🎉 All tests passed!"
    exit 0
fi