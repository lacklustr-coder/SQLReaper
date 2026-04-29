@echo off
title Aikido Security Scanner
color 0E

echo.
echo =========================================
echo   Aikido Security Scanner for SQLReaper
echo =========================================
echo.

:: Check if Aikido CLI is installed
where aikido >nul 2>nul
if errorlevel 1 (
    echo [WARN] Aikido CLI not found!
    echo.
    echo To install Aikido CLI:
    echo   npm install -g @aikidosec/cli
    echo   OR
    echo   pip install aikido-cli
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo [OK] Aikido CLI found
echo.

:menu
echo =========================================
echo   Select Scan Type:
echo =========================================
echo.
echo   1. Quick Dependency Scan
echo   2. Full Security Scan (All)
echo   3. Secrets Detection Only
echo   4. SAST (Code Analysis) Only
echo   5. View Configuration
echo   6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto dep_scan
if "%choice%"=="2" goto full_scan
if "%choice%"=="3" goto secrets_scan
if "%choice%"=="4" goto sast_scan
if "%choice%"=="5" goto view_config
if "%choice%"=="6" goto end

echo [ERROR] Invalid choice. Please select 1-6.
echo.
goto menu

:dep_scan
echo.
echo =========================================
echo   Running Dependency Scan...
echo =========================================
echo.
aikido scan dependencies
echo.
echo Scan completed!
pause
goto menu

:full_scan
echo.
echo =========================================
echo   Running Full Security Scan...
echo =========================================
echo.
aikido scan --all --config aikido.yml
echo.
echo Scan completed!
pause
goto menu

:secrets_scan
echo.
echo =========================================
echo   Running Secrets Detection...
echo =========================================
echo.
aikido scan secrets
echo.
echo Scan completed!
pause
goto menu

:sast_scan
echo.
echo =========================================
echo   Running Code Analysis (SAST)...
echo =========================================
echo.
aikido scan sast
echo.
echo Scan completed!
pause
goto menu

:view_config
echo.
echo =========================================
echo   Current Aikido Configuration
echo =========================================
echo.
if exist aikido.yml (
    type aikido.yml
) else (
    echo [ERROR] aikido.yml not found!
)
echo.
pause
goto menu

:end
echo.
echo Exiting Aikido Scanner. Stay secure!
echo.
