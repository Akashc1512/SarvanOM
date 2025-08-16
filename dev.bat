@echo off
REM Universal Knowledge Hub - Development Script for Windows
REM Usage: dev.bat [command]

if "%1"=="" (
    echo Universal Knowledge Hub - Available Commands:
    echo.
    echo Setup:
    echo   install     - Install all dependencies
    echo   setup       - Complete project setup
    echo.
    echo Development:
    echo   dev         - Start development servers
    echo   dev:frontend- Start frontend only
    echo   dev:backend - Start backend only
    echo.
    echo Testing:
    echo   test        - Run all tests
    echo   test:unit   - Run unit tests
    echo.
    echo Code Quality:
    echo   lint        - Run linting
    echo   format      - Format code
    echo.
    echo Services:
    echo   start:api-gateway    - Start API Gateway
    echo   start:auth-service   - Start Auth service
    echo   start:search-service - Start Search service
    echo   start:synthesis-service - Start Synthesis service
    echo   start:factcheck-service - Start Fact Check service
    echo   start:analytics-service - Start Analytics service
    goto :eof
)

if "%1"=="install" (
    echo Installing Node.js dependencies...
    npm install
    echo Installing Python dependencies...
    .venv\Scripts\pip install -e .[dev,test,security]
    echo Installation complete!
    goto :eof
)

if "%1"=="setup" (
    echo Setting up project...
    npm install
    .venv\Scripts\pip install -e .[dev,test,security]
    if not exist ".env" (
        copy "env.docker.template" ".env"
        echo Created .env file from template. Please configure your environment variables.
    )
    echo Setup complete!
    goto :eof
)

if "%1"=="dev" (
    echo Starting development servers...
    start "Frontend" cmd /k "npm run dev:frontend"
    start "Backend" cmd /k "npm run dev:backend"
    goto :eof
)

if "%1"=="dev:frontend" (
    echo Starting frontend development server...
    npm run dev:frontend
    goto :eof
)

if "%1"=="dev:backend" (
    echo Starting backend development server...
    npm run dev:backend
    goto :eof
)

if "%1"=="test" (
    echo Running all tests...
    npm run test
    goto :eof
)

if "%1"=="test:unit" (
    echo Running unit tests...
    npm run test:unit
    goto :eof
)

if "%1"=="test:database" (
    echo Running database model tests...
    python tests/run_database_tests.py
    goto :eof
)

if "%1"=="validate:database" (
    echo Validating database models...
    python scripts/validate_database_models.py
    goto :eof
)

if "%1"=="lint" (
    echo Running linting...
    npm run lint
    goto :eof
)

if "%1"=="format" (
    echo Formatting code...
    npm run format
    goto :eof
)

if "%1"=="start:api-gateway" (
    echo Starting API Gateway...
    npm run start:api-gateway
    goto :eof
)

if "%1"=="start:auth-service" (
    echo Starting Auth service...
    npm run start:auth-service
    goto :eof
)

if "%1"=="start:search-service" (
    echo Starting Search service...
    npm run start:search-service
    goto :eof
)

if "%1"=="start:synthesis-service" (
    echo Starting Synthesis service...
    npm run start:synthesis-service
    goto :eof
)

if "%1"=="start:factcheck-service" (
    echo Starting Fact Check service...
    npm run start:factcheck-service
    goto :eof
)

if "%1"=="start:analytics-service" (
    echo Starting Analytics service...
    npm run start:analytics-service
    goto :eof
)

echo Unknown command: %1
echo Run 'dev.bat' for available commands 