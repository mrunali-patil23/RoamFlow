@echo off
REM Development script for AI Trip Planner (Windows)
REM Starts both frontend and backend in development mode

echo 🚀 Starting AI Trip Planner Development Environment

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Please copy .env.example to .env and configure your API keys.
    pause
    exit /b 1
)

echo 🐍 Starting Python FastAPI backend...
cd backend

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Start backend server in background
echo 🚀 Starting backend server on http://localhost:8000
start /B python main.py

cd ..

echo ⚛️  Starting React frontend...
cd frontend

REM Install dependencies
echo 📦 Installing Node.js dependencies...
call npm install

REM Start frontend server
echo 🚀 Starting frontend server on http://localhost:5173
start /B npm run dev

cd ..

echo.
echo ✅ Development environment started!
echo 📱 Frontend: http://localhost:5173
echo 🔧 Backend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services
pause >nul

REM Kill background processes (simplified - may need adjustment)
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul