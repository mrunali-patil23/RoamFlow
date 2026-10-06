#!/bin/bash

# Production Build Script for AI Trip Planner
# This script builds both frontend and backend for production deployment

set -e  # Exit on any error

echo "🚀 Starting production build for AI Trip Planner..."

# Check if required environment variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ] || [ -z "$SERP_API_KEY" ] || [ -z "$GEMINI_API_KEY" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ Error: Required environment variables are not set."
    echo "Please ensure the following variables are configured:"
    echo "  - SUPABASE_URL"
    echo "  - SUPABASE_KEY"
    echo "  - SERP_API_KEY"
    echo "  - GEMINI_API_KEY"
    echo "  - SECRET_KEY"
    exit 1
fi

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo "🧪 Running backend tests..."
python -m pytest tests/ -v --tb=short

echo "📦 Installing frontend dependencies..."
cd ../frontend
npm ci

echo "🧪 Running frontend tests..."
npm test -- --run

echo "🏗️ Building frontend for production..."
npm run build

echo "✅ Production build completed successfully!"
echo ""
echo "📋 Deployment checklist:"
echo "  ✓ Backend dependencies installed"
echo "  ✓ Backend tests passed"
echo "  ✓ Frontend dependencies installed"
echo "  ✓ Frontend tests passed"
echo "  ✓ Frontend built for production"
echo ""
echo "📁 Build artifacts:"
echo "  - Frontend: frontend/dist/"
echo "  - Backend: backend/ (ready for deployment)"
echo ""
echo "🚀 Ready for deployment!"