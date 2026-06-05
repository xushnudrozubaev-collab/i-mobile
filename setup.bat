@echo off
REM i-Mobile CRM Setup Script for Windows
REM This script helps set up the project with all necessary configurations

setlocal enabledelayedexpansion

echo.
echo ====================================
echo i-Mobile CRM - Setup Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version
echo OK

REM Check if pip is available
echo [2/5] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)
echo OK

REM Create virtual environment
echo [3/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo OK
)

REM Activate virtual environment
echo [4/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo OK

REM Install dependencies
echo [5/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure database settings
echo 2. Run: python manage.py migrate
echo 3. Run: python manage.py createsuperuser
echo 4. Run: python manage.py runserver
echo.
echo Documentation: See README.md for more information
echo.
pause
