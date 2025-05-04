@echo off
echo EOTIR Manager Runner
echo ===================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    echo.
    pause
    exit /b 1
)

REM List components if no arguments are provided
if "%~1"=="" (
    echo Available options:
    echo   list        - List all available components
    echo   all         - Run all components in sequence
    echo   scenarios   - Process scenarios only
    echo   scraper     - Run scenario scraper only
    echo   indexer     - Run scenario indexer only
    echo   llm         - Run LLM data extraction only
    echo   report      - Generate combined report only
    echo.
    echo Example: %~nx0 scenarios
    echo.
    python eotir_manager.py --list
    pause
    exit /b 0
)

REM Run the selected component
if "%~1"=="list" (
    python eotir_manager.py --list
) else if "%~1"=="all" (
    echo Running all components in sequence...
    python eotir_manager.py --all %2 %3 %4 %5 %6 %7 %8 %9
) else (
    echo Running %~1 component...
    python eotir_manager.py --component %~1 --args %2 %3 %4 %5 %6 %7 %8 %9
)

echo.
if %ERRORLEVEL% neq 0 (
    echo Component execution failed. See logs for details.
) else (
    echo Component executed successfully!
)

pause
