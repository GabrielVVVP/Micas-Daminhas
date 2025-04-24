@echo off
cd /d "%~dp0"

REM Navigate to the project directory
cd "%~dp0"

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed or not added to PATH. Please install Git and try again.
    pause
    exit /b
)

REM Pull updates from the origin main branch
echo Pulling updates from origin main...
git pull origin main

if %errorlevel% neq 0 (
    echo Failed to pull updates. Please check your Git configuration or network connection.
    pause
    exit /b
)

echo Updates pulled successfully!
pause