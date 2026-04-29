@echo off
title SQLReaper DEBUG - Finding Issues
color 0C

echo.
echo ===============================================================================
echo   SQLReaper DEBUG MODE
echo ===============================================================================
echo.
echo This debug script will help identify the issue...
echo.

:: Test 1: Check we're in right directory
echo [TEST 1] Current directory:
cd
echo.

:: Test 2: Check Python
echo [TEST 2] Checking for Python...
where python
if errorlevel 1 (
    echo [FAIL] Python not found in PATH!
    pause
    exit /b 1
)
echo.

:: Test 3: Python version
echo [TEST 3] Python version:
python --version
echo.

:: Test 4: Check if requirements.txt exists
echo [TEST 4] Checking requirements.txt...
if exist requirements.txt (
    echo [OK] requirements.txt found
    dir requirements.txt
) else (
    echo [FAIL] requirements.txt NOT found!
    pause
    exit /b 1
)
echo.

:: Test 5: Check if sqlmap_gui folder exists
echo [TEST 5] Checking sqlmap_gui folder...
if exist sqlmap_gui (
    echo [OK] sqlmap_gui folder found
    dir sqlmap_gui\app.py
) else (
    echo [FAIL] sqlmap_gui folder NOT found!
    pause
    exit /b 1
)
echo.

:: Test 6: Check Flask import
echo [TEST 6] Testing Flask import...
python -c "import flask; print('Flask version:', flask.__version__)"
if errorlevel 1 (
    echo [FAIL] Flask not installed!
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)
echo.

:: Test 7: Check JWT import
echo [TEST 7] Testing JWT import...
python -c "import jwt; print('JWT installed OK')" 2>&1
if errorlevel 1 (
    echo [WARN] PyJWT may not be installed
)
echo.

:: Test 8: Check flask_socketio import
echo [TEST 8] Testing flask_socketio import...
python -c "import flask_socketio; print('SocketIO installed OK')" 2>&1
if errorlevel 1 (
    echo [WARN] flask-socketio may not be installed
)
echo.

:: Test 9: Try importing the app
echo [TEST 9] Testing if app.py can be imported...
python -c "import sys; sys.path.insert(0, 'sqlmap_gui'); import app; print('App module loaded OK')" 2>&1
echo.

echo ===============================================================================
echo   Tests Complete
echo ===============================================================================
echo.
echo If all tests passed, the issue might be during startup.
echo Let's try to run the app with full error output...
echo.
pause

echo.
echo Starting app with full debug output...
echo.
cd /d "%~dp0"
python -u sqlmap_gui/app.py
echo.
echo.
echo App exited with code: %ERRORLEVEL%
echo.
pause
