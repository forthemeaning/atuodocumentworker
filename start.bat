@echo off
title DocTool Web Server

echo ============================================
echo  DocTool - Web Server Launcher
echo ============================================
echo.

:: Switch to project root
cd /d "%~dp0"

:: Use conda env if available
set PYTHON_CMD=python
if exist "C:\Users\YxYxi\anaconda3\envs\autowork\python.exe" (
    set PYTHON_CMD=C:\Users\YxYxi\anaconda3\envs\autowork\python.exe
    echo [INFO] Using autowork conda environment
)

%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

:: Check/install Flask
%PYTHON_CMD% -c "import flask" 2>nul
if errorlevel 1 (
    echo [INFO] Installing Flask...
    %PYTHON_CMD% -m pip install flask -q
    if errorlevel 1 (
        echo [ERROR] Flask install failed
        pause
        exit /b 1
    )
    echo [OK] Flask installed
)

:: Check/install pandas + openpyxl
%PYTHON_CMD% -c "import pandas, openpyxl" 2>nul
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    %PYTHON_CMD% -m pip install pandas openpyxl -q
    if errorlevel 1 (
        echo [ERROR] Dependency install failed
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
)

echo.
echo [STARTING] Web server...
echo.
echo Open: http://127.0.0.1:5000
echo Close this window to stop the server.
echo.

:: Open browser
start /B "" http://127.0.0.1:5000

:: Start Flask
%PYTHON_CMD% web/app.py

pause
