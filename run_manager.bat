@echo off
REM EOTIR Scenario Manager - Windows Batch Script
REM This script runs the scenario manager with the provided arguments

echo EOTIR Scenario Manager
echo =====================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.11 or later
    pause
    exit /b 1
)

REM Run the scenario manager with all arguments passed to this script
python main.py %*

if errorlevel 1 (
    echo.
    echo Scenario manager completed with errors.
) else (
    echo.
    echo Scenario manager completed successfully.
)

pause
