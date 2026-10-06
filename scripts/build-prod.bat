@echo off
REM Production Build Script for AI Trip Planner (Windows)
REM This script builds both frontend and backend for production deployment

echo 🚀 Starting production build for AI Trip Planner...

REM Check if required environment variables are set
if "%SUPABASE_URL%"=="" (
    echo ❌ Error: SUPABASE_URL environment variable is not set.
    goto :error
)
if "%SUPABASE_KEY%"=="" (
    echo ❌ Error: SUPABASE_KEY environment variable is not set.
    goto :error
)
if "%SERP_API_KEY%"=="" (
    echo ❌ Error: SERP_API_KEY environment variable is not set.
    goto :error
)
if "%GEMINI_API_KEY%"=="" (
    echo ❌ Error: GEMINI_API_KEY environment variable is not set.
    goto :error
)
if "%SECRET_KEY%"=="" (
    echo ❌ Error: SECRET_KEY environment variable is not set.
    goto :error
)

REM Set production environment
set ENVIRONMENT=production
set DEBUG=false

echo 📦 Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 goto :error

echo 🧪 Running backend tests...
python -m pytest tests/ -v --tb=short
if errorlevel 1 goto :error

echo 📦 Installing frontend dependencies...
cd ..\frontend
call npm ci
if errorlevel 1 goto :error

echo 🧪 Running frontend tests...
call npm test -- --run
if errorlevel 1 goto :error

echo 🏗️ Building frontend for production...
call npm run build
if errorlevel 1 goto :error

echo ✅ Production build completed successfully!
echo.
echo 📋 Deployment checklist:
echo   ✓ Backend dependencies installed
echo   ✓ Backend tests passed
echo   ✓ Frontend dependencies installed
echo   ✓ Frontend tests passed
echo   ✓ Frontend built for production
echo.
echo 📁 Build artifacts:
echo   - Frontend: frontend\dist\
echo   - Backend: backend\ (ready for deployment)
echo.
echo 🚀 Ready for deployment!
goto :end

:error
echo ❌ Build failed! Please check the error messages above.
echo.
echo Please ensure the following environment variables are configured:
echo   - SUPABASE_URL
echo   - SUPABASE_KEY
echo   - SERP_API_KEY
echo   - GEMINI_API_KEY
echo   - SECRET_KEY
exit /b 1

:end