@echo off
title SQLReaper v2.1 Advanced - API Demo
color 0E

echo.
echo ===============================================================================
echo   SQLReaper v2.1 Advanced - Interactive API Demo
echo ===============================================================================
echo.
echo This demo will showcase the advanced features:
echo   - JWT Authentication
echo   - AI-Powered Vulnerability Analysis
echo   - WAF Detection and Bypass
echo   - Exploitation Chain Discovery
echo   - Next-Step Prediction
echo.
echo Make sure SQLReaper is running before starting the demo!
echo (Run start.bat in another window if not already running)
echo.
pause

:: Check if requests is installed
python -c "import requests" >nul 2>nul
if errorlevel 1 (
    echo [WARN] 'requests' library not found. Installing...
    pip install requests --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install requests library
        pause
        exit /b 1
    )
    echo [OK] requests library installed
)

echo.
echo Starting demo...
echo.
echo ===============================================================================
echo.

python demo_api.py

echo.
echo ===============================================================================
echo   Demo Complete
echo ===============================================================================
echo.
echo For more information:
echo   - View FEATURES.md for complete API documentation
echo   - Check PROJECT_STATUS.md for usage examples
echo   - Review CHANGELOG.md for all features
echo.
pause
