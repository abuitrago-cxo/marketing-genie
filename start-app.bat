@echo off
title Gemini Fullstack LangGraph - Setup & Start

echo ========================================
echo  Gemini Fullstack LangGraph Quickstart
echo ========================================
echo.

REM Check if this is first time setup
set FIRST_TIME=0

REM Check if backend dependencies are installed
echo Checking backend dependencies...
cd backend
pip show langgraph >nul 2>&1
if %errorlevel% neq 0 (
    echo Backend dependencies not found. Installing...
    set FIRST_TIME=1
    pip install .
    if %errorlevel% neq 0 (
        echo Error: Failed to install backend dependencies
        pause
        exit /b 1
    )
    echo ✓ Backend dependencies installed successfully
) else (
    echo ✓ Backend dependencies already installed
)
cd ..

REM Check if frontend dependencies are installed
echo Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo Frontend dependencies not found. Installing...
    set FIRST_TIME=1
    cd frontend
    npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install frontend dependencies
        pause
        exit /b 1
    )
    echo ✓ Frontend dependencies installed successfully
    cd ..
) else (
    echo ✓ Frontend dependencies already installed
)

REM Check for .env file
echo.
echo Checking API key configuration...
if not exist "backend\.env" (
    echo ⚠️  WARNING: No .env file found in backend directory
    echo.
    echo Please create backend\.env with your Gemini API key:
    echo GEMINI_API_KEY="your_actual_api_key_here"
    echo.
    echo Get your API key from: https://aistudio.google.com/app/apikey
    echo.
) else (
    echo ✓ .env file found
)

echo.
if %FIRST_TIME%==1 (
    echo ✓ Setup completed successfully!
    echo.
)

echo ========================================
echo  Starting Development Servers
echo ========================================
echo.
echo Frontend: http://localhost:5173/app/
echo Backend:  http://127.0.0.1:2024
echo.
echo Press Ctrl+C in any window to stop both servers
echo.

REM Start backend server in a new window
start "Backend Server - LangGraph" cmd /k "cd /d %~dp0backend && echo Starting backend server... && langgraph dev"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in a new window
start "Frontend Server - React/Vite" cmd /k "cd /d %~dp0frontend && echo Starting frontend server... && npm run dev"

echo.
echo Both servers are starting in separate windows...
echo.
echo To stop the servers:
echo 1. Close both command prompt windows, or
echo 2. Press Ctrl+C in each window
echo.
echo Press any key to close this window...
pause >nul 