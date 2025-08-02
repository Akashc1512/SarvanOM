@echo off
REM End-to-End Test Runner for Windows
REM This batch file runs comprehensive E2E tests for the real backend pipeline

echo.
echo ==================================================
echo    Real Backend Pipeline E2E Test Runner
echo ==================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the project root
if not exist "services" (
    echo ERROR: Please run this script from the project root directory
    echo Current directory: %CD%
    echo Expected to find 'services' directory
    pause
    exit /b 1
)

REM Check if test file exists
if not exist "tests\e2e\test_real_backend_pipeline.py" (
    echo ERROR: Test file not found
    echo Expected: tests\e2e\test_real_backend_pipeline.py
    pause
    exit /b 1
)

echo Checking environment...
echo.

REM Check if required packages are installed
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo Installing pytest...
    pip install pytest
)

python -c "import httpx" >nul 2>&1
if errorlevel 1 (
    echo Installing httpx...
    pip install httpx
)

echo.
echo Running E2E tests...
echo.

REM Run the test runner script
python run_e2e_tests.py %*

if errorlevel 1 (
    echo.
    echo ==================================================
    echo    Tests completed with errors
    echo ==================================================
    echo.
    echo Troubleshooting tips:
    echo 1. Check if all services are running
    echo 2. Verify environment variables are set
    echo 3. Check the test logs above for specific errors
    echo 4. Run with --verbose flag for more details
    echo.
    echo Command: python run_e2e_tests.py --verbose
    echo.
) else (
    echo.
    echo ==================================================
    echo    All tests completed successfully!
    echo ==================================================
    echo.
    echo Next steps:
    echo 1. Review test results and performance metrics
    echo 2. Validate response quality manually
    echo 3. Monitor system resources
    echo 4. Update documentation if needed
    echo.
)

pause 