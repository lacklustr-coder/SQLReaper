@echo off
title SQLReaper v2.1 Advanced - First-Time Setup
color 0B

echo.
echo ===============================================================================
echo   SQLReaper v2.1 Advanced - First-Time Setup Wizard
echo ===============================================================================
echo.
echo This wizard will help you set up SQLReaper for the first time.
echo.
pause

:: Check Python
echo.
echo [1/5] Checking Python installation...
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python %PYVER% detected
echo.

:: Upgrade pip
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARN] Failed to upgrade pip, continuing with current version...
) else (
    echo [OK] pip upgraded successfully
)
echo.

:: Install dependencies
echo [3/5] Installing dependencies...
echo This may take a few minutes...
echo.

if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies!
        echo.
        echo Please try manually:
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] All dependencies installed successfully!
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

:: Create directories
echo.
echo [4/5] Creating required directories...
if not exist uploads mkdir uploads
if not exist results mkdir results
if not exist profiles mkdir profiles
echo [OK] Directories created

:: Initialize database
echo.
echo [5/5] Initializing database and features...
python -c "from sqlmap_gui.init_features import initialize_all_features; from flask import Flask; app = Flask(__name__); initialize_all_features(app); print('[OK] Database initialized')" 2>nul
if errorlevel 1 (
    echo [INFO] Database will be initialized on first run
) else (
    echo [OK] Database initialized successfully
)

:: Setup complete
echo.
echo ===============================================================================
echo   Setup Complete!
echo ===============================================================================
echo.
echo SQLReaper v2.1 Advanced is ready to use!
echo.
echo Next steps:
echo.
echo   1. Run start.bat to launch the application
echo   2. Open your browser to: http://localhost:5000
echo   3. Login with default credentials:
echo        Username: admin
echo        Password: admin123
echo.
echo   4. IMPORTANT: Change the default password immediately!
echo.
echo Optional configuration:
echo.
echo   - Set SQLMAP_PATH environment variable to your sqlmap installation
echo   - Set JWT_SECRET environment variable for production use
echo   - Configure proxy/Tor settings in the web interface
echo.
echo Documentation:
echo.
echo   - README.md - Getting started guide
echo   - FEATURES.md - Complete feature list with examples
echo   - CHANGELOG.md - Version history
echo   - PROJECT_STATUS.md - Testing checklist
echo.
echo Run demo_api.py to see the API in action!
echo.
echo ===============================================================================
echo.

pause
echo.
echo Would you like to start SQLReaper now? (Y/N)
choice /c YN /n /m "Press Y for Yes, N for No: "

if errorlevel 2 goto :end
if errorlevel 1 goto :start

:start
echo.
echo Starting SQLReaper...
echo.
call start.bat
goto :end

:end
echo.
echo Setup wizard finished. You can run start.bat anytime to launch SQLReaper.
echo.
pause
