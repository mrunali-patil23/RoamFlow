@echo off
echo Setting up AI Travel Planner backend...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "backend\venv" (
    echo Creating Python virtual environment...
    python -m venv backend\venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call backend\venv\Scripts\activate
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Backend setup complete!
echo.
echo To start the backend server:
echo   cd backend
echo   venv\Scripts\activate
echo   python -m uvicorn main:app --reload
echo.
pause