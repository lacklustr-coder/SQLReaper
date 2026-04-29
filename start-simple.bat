@echo off
title SQLReaper - Simple Launcher
color 0A

echo.
echo ===============================================================================
echo   SQLReaper v2.1 Advanced - Simple Launcher
echo ===============================================================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

:: Check if app exists
if not exist "sqlmap_gui\app.py" (
    echo ERROR: Cannot find sqlmap_gui\app.py
    echo Make sure you're running this from the SQLReaper directory.
    echo.
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies (this may take a minute)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Try running manually: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.
echo ===============================================================================
echo   Starting SQLReaper...
echo ===============================================================================
echo.
echo   Web Interface: http://localhost:5000
echo   Login: admin / admin123
echo.
echo   Press Ctrl+C to stop the server
echo ===============================================================================
echo.

:: Run the app
python sqlmap_gui\app.py

:: Check exit code
if errorlevel 1 (
    echo.
    echo ===============================================================================
    echo   ERROR: Server crashed or failed to start
    echo ===============================================================================
    echo.
    echo Common fixes:
    echo   1. Reinstall dependencies: pip install -r requirements.txt --force-reinstall
    echo   2. Check if port 5000 is available
    echo   3. Check error messages above
    echo.
)

pause
