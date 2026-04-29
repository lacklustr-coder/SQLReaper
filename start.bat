@echo off
title SQLReaper v2.1 Advanced - Enterprise Penetration Testing Framework
color 0A

echo.
echo ===============================================================================
echo   _____ ____    __    ____
echo  / ___// __ \  / /   / __ \___  ____ _____  ___  _____
echo  \__ \/ / / / / /   / /_/ / _ \/ __ `/ __ \/ _ \/ ___/
echo ___/ / /_/ / / /___/ _, _/  __/ /_/ / /_/ /  __/ /
echo/____/\___\_\/_____/_/ |_|\___/\__,_/ .___/\___/_/
echo                                    /_/
echo.
echo   SQLReaper v2.1 Advanced - Enterprise Penetration Testing Framework
echo   AI-Powered Analysis ^| Advanced WAF Bypass ^| Real-Time Monitoring
echo ===============================================================================
echo.

:: Check Python
echo [1/6] Checking Python installation...
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.8+ first.
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python %PYVER% found

:: Check and install dependencies
echo.
echo [2/6] Checking dependencies...
python -c "import flask, jwt, flask_socketio" >nul 2>nul
if errorlevel 1 (
    echo [WARN] Missing dependencies detected. Installing...
    echo.
    if exist requirements.txt (
        echo Installing from requirements.txt...
        pip install -r requirements.txt --quiet
        if errorlevel 1 (
            echo [ERROR] Failed to install dependencies!
            echo Try manually: pip install -r requirements.txt
            pause
            exit /b 1
        )
        echo [OK] All dependencies installed successfully
    ) else (
        echo [ERROR] requirements.txt not found!
        pause
        exit /b 1
    )
) else (
    echo [OK] All dependencies found
)

:: Check sqlmap
echo.
echo [3/6] Checking sqlmap...
if defined SQLMAP_PATH (
    if exist "%SQLMAP_PATH%" (
        echo [OK] sqlmap found at: %SQLMAP_PATH%
    ) else (
        echo [WARN] SQLMAP_PATH set but path not found: %SQLMAP_PATH%
        echo [INFO] You can configure sqlmap path in Settings after launch
    )
) else (
    echo [INFO] SQLMAP_PATH not set. Configure in Settings after launch or set environment variable
)

:: Create needed directories
echo.
echo [4/6] Setting up directories...
if not exist uploads mkdir uploads
if not exist results mkdir results
if not exist profiles mkdir profiles
if not exist sqlmap_gui\__pycache__ (
    echo [OK] Created required directories
) else (
    echo [OK] Directories ready
)

:: Set environment variables for optimal performance
echo.
echo [5/6] Configuring environment...
set PYTHONUNBUFFERED=1
set FLASK_APP=sqlmap_gui/app.py
if not defined JWT_SECRET (
    echo [WARN] JWT_SECRET not set. Using auto-generated secret.
    echo [INFO] For production, set JWT_SECRET environment variable!
)
echo [OK] Environment configured

:: Display startup information
echo.
echo [6/6] Starting SQLReaper...
echo.
echo ===============================================================================
echo   STARTUP INFORMATION
echo ===============================================================================
echo.
echo   Web Interface:     http://localhost:5000
echo   API Documentation: http://localhost:5000/api/health/features
echo.
echo   Default Credentials:
echo     Username: admin
echo     Password: admin123
echo     [WARNING] Change password immediately in production!
echo.
echo   Features Enabled:
echo     [+] AI-Powered Vulnerability Analysis
echo     [+] Advanced WAF Bypass Engine
echo     [+] JWT Authentication (24h sessions)
echo     [+] Real-Time WebSocket Monitoring
echo     [+] Exploitation Chain Discovery
echo     [+] Custom Payload Library
echo     [+] Multi-Format Reporting
echo.
echo ===============================================================================
echo   Press Ctrl+C to stop the server
echo ===============================================================================
echo.

cd /d "%~dp0"
python sqlmap_gui/app.py

if errorlevel 1 (
    echo.
    echo ===============================================================================
    echo   [ERROR] Server failed to start or crashed!
    echo ===============================================================================
    echo.
    echo Possible causes:
    echo   1. Port 5000 already in use (try closing other applications)
    echo   2. Missing dependencies (run: pip install -r requirements.txt)
    echo   3. Database permission issues (check results/ folder permissions)
    echo   4. Python version incompatibility (requires Python 3.8+)
    echo.
    echo For detailed error info, check the output above.
    echo.
    echo Quick fixes:
    echo   - Reinstall dependencies: pip install -r requirements.txt --force-reinstall
    echo   - Delete database cache: del sqlmap_gui\scans.db
    echo   - Check Python version: python --version
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ===============================================================================
    echo   Server stopped gracefully
    echo ===============================================================================
    echo.
    echo Thank you for using SQLReaper v2.1 Advanced!
    echo.
    echo For support and documentation:
    echo   - README.md - Getting started guide
    echo   - FEATURES.md - Complete feature documentation
    echo   - CHANGELOG.md - What's new in this version
    echo   - PROJECT_STATUS.md - Project overview and testing
    echo.
    pause
)
