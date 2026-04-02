@echo off
title SQLMap GUI v2.1
color 0A

echo.
echo =========================================
echo   SQLMap GUI v2.1 - Starting...
echo =========================================
echo.

:: Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python first.
    pause
    exit /b 1
)
echo [OK] Python found

:: Check Flask
python -c "import flask" >nul 2>nul
if errorlevel 1 (
    echo [WARN] Flask not found, installing...
    pip install flask werkzeug
    if errorlevel 1 (
        echo [ERROR] Failed to install Flask!
        pause
        exit /b 1
    )
    echo [OK] Flask installed
) else (
    echo [OK] Flask found
)

:: Check sqlmap (generic check - user should configure in settings)
echo [INFO] Configure sqlmap path in Settings after launch

:: Create needed directories
if not exist uploads mkdir uploads
if not exist results mkdir results
if not exist profiles mkdir profiles

echo.
echo =========================================
echo   Launching SQLMap GUI on port 5000
echo =========================================
echo.
echo Press Ctrl+C to stop the server.
echo.

cd /d "%~dp0"
set PYTHONUNBUFFERED=1
python sqlmap_gui/app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start or crashed.
    echo Press any key to exit...
    pause
)