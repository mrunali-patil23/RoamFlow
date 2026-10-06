#!/bin/bash

# Development script for AI Trip Planner
# Starts both frontend and backend in development mode

echo "🚀 Starting AI Trip Planner Development Environment"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Function to start backend
start_backend() {
    echo "🐍 Starting Python FastAPI backend..."
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Start backend server
    echo "🚀 Starting backend server on http://localhost:8000"
    python main.py &
    BACKEND_PID=$!
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "⚛️  Starting React frontend..."
    cd frontend
    
    # Install dependencies
    echo "📦 Installing Node.js dependencies..."
    npm install
    
    # Start frontend server
    echo "🚀 Starting frontend server on http://localhost:5173"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
}

# Start both services
start_backend
start_frontend

echo ""
echo "✅ Development environment started!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait