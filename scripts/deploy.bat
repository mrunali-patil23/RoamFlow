@echo off
REM AI Trip Planner Deployment Script (Windows)
REM This script handles the complete deployment process

setlocal enabledelayedexpansion

REM Configuration
set DEPLOYMENT_TYPE=%1
set ENVIRONMENT=%2

if "%DEPLOYMENT_TYPE%"=="" set DEPLOYMENT_TYPE=docker
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production

echo 🚀 AI Trip Planner Deployment Script
echo ======================================
echo Deployment Type: %DEPLOYMENT_TYPE%
echo Environment: %ENVIRONMENT%
echo.

REM Function to check environment variables
call :check_env_vars
if errorlevel 1 goto :error

REM Run tests (skip in CI/CD environments)
if not "%SKIP_TESTS%"=="true" (
    call :run_tests
    if errorlevel 1 goto :error
)

REM Deploy based on type
if "%DEPLOYMENT_TYPE%"=="docker" (
    call :deploy_docker
    if errorlevel 1 goto :error
) else if "%DEPLOYMENT_TYPE%"=="manual" (
    call :deploy_manual
    if errorlevel 1 goto :error
) else (
    echo ❌ Unknown deployment type: %DEPLOYMENT_TYPE%
    echo Supported types: docker, manual
    goto :error
)

REM Show status
call :show_status

echo.
echo 🎉 Deployment completed successfully!
goto :end

:check_env_vars
echo 🔍 Checking environment variables...

set missing_vars=
if "%SUPABASE_URL%"=="" set missing_vars=!missing_vars! SUPABASE_URL
if "%SUPABASE_KEY%"=="" set missing_vars=!missing_vars! SUPABASE_KEY
if "%SERP_API_KEY%"=="" set missing_vars=!missing_vars! SERP_API_KEY
if "%GEMINI_API_KEY%"=="" set missing_vars=!missing_vars! GEMINI_API_KEY
if "%SECRET_KEY%"=="" set missing_vars=!missing_vars! SECRET_KEY

if not "!missing_vars!"=="" (
    echo ❌ Missing required environment variables:
    for %%v in (!missing_vars!) do echo   - %%v
    echo.
    echo Please set these variables in your .env file or environment.
    exit /b 1
)

echo ✅ All required environment variables are set
exit /b 0

:run_tests
echo 🧪 Running tests...

echo Running backend tests...
cd backend
python -m pytest tests/ -v --tb=short
if errorlevel 1 (
    echo ❌ Backend tests failed
    exit /b 1
)
cd ..

echo Running frontend tests...
cd frontend
call npm test -- --run
if errorlevel 1 (
    echo ❌ Frontend tests failed
    exit /b 1
)
cd ..

echo ✅ All tests passed
exit /b 0

:deploy_docker
echo 🐳 Deploying with Docker...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed
    exit /b 1
)

REM Stop existing containers
echo Stopping existing containers...
docker-compose down --remove-orphans

REM Build and start containers
echo Building and starting containers...
if "%ENVIRONMENT%"=="production" (
    docker-compose -f docker-compose.prod.yml up --build -d
) else (
    docker-compose up --build -d
)

REM Wait for services to be healthy
echo Waiting for services to be healthy...
timeout /t 30 /nobreak >nul

echo ✅ Docker deployment completed successfully
exit /b 0

:deploy_manual
echo 📦 Manual deployment...

echo Building frontend...
cd frontend
call npm ci
call npm run build
cd ..

echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo ✅ Manual build completed
echo Note: You need to manually start the services:
echo   Backend: cd backend ^&^& uvicorn main:app --host 0.0.0.0 --port 8000
echo   Frontend: Serve the frontend/dist directory with a web server
exit /b 0

:show_status
echo 📊 Deployment Status
echo ==================

if "%DEPLOYMENT_TYPE%"=="docker" (
    echo Docker containers:
    docker-compose ps
    echo.
    
    echo Service URLs:
    echo   Frontend: http://localhost
    echo   Backend API: http://localhost:8000
    echo   Health Check: http://localhost:8000/health
)
exit /b 0

:error
echo ❌ Deployment failed! Please check the error messages above.
exit /b 1

:end