@echo off
title PALI 1 - Local Helper
echo Starting PALI 1 Local Engine...
echo This may take a moment to initialize...

cd backend
python -c "import sys; print('Checking Python...')" >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found! Please install Python 3.9+ from python.org
    pause
    exit
)

:: Install dependencies silently if needed
pip install -r ../requirements.txt >nul 2>&1

:: Run app
start "" "http://localhost:8000"
python main.py
