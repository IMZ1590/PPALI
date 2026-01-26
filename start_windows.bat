@echo off
SETLOCAL EnableExtensions EnableDelayedExpansion

title PPALI - Windows Launcher

echo ===================================================
echo   PPALI (Peak-based PCA Analysis for Ligand Interactions)
echo   Windows Automatic Launcher
echo ===================================================

:: 1. Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found.
    echo Please install Python (3.9+) from https://www.python.org/downloads/
    echo and ensure "Add Python to PATH" is checked during installation.
    pause
    exit /b
)

:: 2. Check/Create Virtual Environment
IF NOT EXIST "venv" (
    echo [INFO] Creating virtual environment (venv)...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
    echo [INFO] Virtual environment created.
) else (
    echo [INFO] Virtual environment found.
)

:: 3. Activate Venv and Install Requirements
echo [INFO] Checking dependencies...
call venv\Scripts\activate.bat

:: Install Requirements if not skipped (can be optimized, but safer to always check)
pip install -r requirements.txt >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b
)
echo [INFO] Dependencies are ready.

:: 4. Run the Application
echo.
echo [START] Launching Server...
echo Open your browser to: http://localhost:8000
echo.

cd backend
python main.py

pause
