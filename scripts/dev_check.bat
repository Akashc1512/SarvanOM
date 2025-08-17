@echo off
REM SarvanOM Development Environment Check Script (Windows Batch)
REM ============================================================
REM This script verifies the development environment is properly configured

echo SarvanOM Development Environment Check (Windows Batch)
echo =====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python is available
) else (
    echo ✗ Python not found
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Node.js is available
) else (
    echo ✗ Node.js not found
)

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Docker is available
) else (
    echo ✗ Docker not found or not running
)

echo.
echo Running comprehensive environment check...
echo.

REM Run the Python script
python scripts\dev_check.py
if %errorlevel% equ 0 (
    echo.
    echo ✓ Environment check completed successfully
) else (
    echo.
    echo ✗ Environment check failed
    exit /b 1
)

echo.
echo Alternative commands:
echo   python scripts\dev_check.py    # Direct Python execution
echo   .\scripts\dev_check.ps1        # PowerShell wrapper
echo   .\scripts\dev_check.bat        # Windows batch file
echo   make doctor                    # Make command (if available)
