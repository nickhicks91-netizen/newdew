@echo off
REM Build EchoZero Standalone Application for Windows
REM
REM This script creates a standalone executable for EchoZero
REM that bundles Python, all dependencies, and the application code.
REM
REM Usage:
REM   build_standalone.bat

echo ==========================================
echo   EchoZero Standalone Build Script
echo ==========================================
echo.

REM Check Python
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.8+
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Install package in development mode
echo Installing EchoZero package...
pip install -e .

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Build standalone executable
echo.
echo Building standalone application...
echo This may take several minutes...
echo.

pyinstaller launcher.spec --clean

REM Check if build succeeded
if exist "dist\EchoZero" (
    echo.
    echo ==========================================
    echo   Build successful!
    echo ==========================================
    echo.
    echo Standalone application created in: dist\EchoZero\
    echo.
    echo To run:
    echo   cd dist\EchoZero
    echo   EchoZero.exe
    echo.
    echo To distribute:
    echo   1. Zip the dist\EchoZero folder
    echo   2. Share with users
    echo   3. Users just extract and run EchoZero.exe
    echo.
) else (
    echo Build failed. Check output above for errors.
    exit /b 1
)
