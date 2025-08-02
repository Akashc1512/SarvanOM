@echo off
echo Starting SarvanOM Docker services...
echo.
echo Checking Docker...
docker --version
if %errorlevel% neq 0 (
    echo ERROR: Docker not accessible
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo.
echo Starting services...
docker compose --env-file .env.docker up --build -d
if %errorlevel% equ 0 (
    echo.
    echo Services started successfully!
    echo.
    echo Access your services at:
    echo   Frontend: http://localhost:3000
    echo   Backend:  http://localhost:8000
    echo   Ollama:   http://localhost:11434
    echo.
    echo Run '.\docker-windows.bat health' to check service health
) else (
    echo Failed to start services
    pause
)
