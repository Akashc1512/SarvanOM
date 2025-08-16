@echo off
REM =============================================================================
REM SarvanOM Docker Management for Windows 11
REM Optimized for Docker Desktop with WSL2 backend
REM =============================================================================

setlocal enabledelayedexpansion

echo.
echo =============================================================================
echo SarvanOM Docker Management for Windows 11
echo =============================================================================
echo.

if "%1"=="" goto help

if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="build" goto build
if "%1"=="logs" goto logs
if "%1"=="clean" goto clean
if "%1"=="restart" goto restart
if "%1"=="health" goto health
if "%1"=="test" goto test
if "%1"=="status" goto status
if "%1"=="setup" goto setup
goto help

:help
echo Available commands:
echo   up      - Start all services with .env.docker
echo   down    - Stop all services
echo   build   - Build all services
echo   logs    - Show logs for all services
echo   clean   - Remove all containers, networks, and volumes
echo   restart - Restart all services
echo   health  - Check health of all services
echo   test    - Run comprehensive Docker health tests
echo   status  - Show service status
echo   setup   - Setup data directories and environment
echo.
echo Example: docker-windows.bat up
goto end

:setup
echo Setting up SarvanOM environment...
if not exist "data" mkdir data
if not exist "data\postgres" mkdir data\postgres
if not exist "data\redis" mkdir data\redis
if not exist "data\meilisearch" mkdir data\meilisearch
if not exist "data\arangodb" mkdir data\arangodb
if not exist "data\arangodb-apps" mkdir data\arangodb-apps
if not exist "data\qdrant" mkdir data\qdrant
if not exist "data\ollama" mkdir data\ollama
if not exist ".env.docker" (
    echo Creating .env.docker from template...
    copy env.docker.template .env.docker
    echo .env.docker created. Please review and update as needed.
) else (
    echo .env.docker already exists.
)
echo Setup completed.
goto end

:up
echo Starting SarvanOM services with .env.docker...
docker compose --env-file .env.docker up --build -d
if %errorlevel% equ 0 (
    echo.
    echo Services started successfully!
    echo.
    echo Access your services at:
    echo   Frontend: http://localhost:3000
    echo   Backend:  http://localhost:8004
    echo   Ollama:   http://localhost:11434
    echo   Meilisearch: http://localhost:7700
    echo   ArangoDB: http://localhost:8529
    echo   Qdrant:   http://localhost:6333
    echo.
    echo Run 'docker-windows.bat health' to check service health.
    echo Run 'docker-windows.bat logs' to view service logs.
) else (
    echo Failed to start services. Check Docker Desktop is running.
)
goto end

:down
echo Stopping SarvanOM services...
docker compose down
if %errorlevel% equ 0 (
    echo Services stopped successfully.
) else (
    echo Failed to stop services.
)
goto end

:build
echo Building SarvanOM services...
docker compose --env-file .env.docker build
if %errorlevel% equ 0 (
    echo Build completed successfully.
) else (
    echo Build failed. Check for errors above.
)
goto end

:logs
echo Showing logs for all services...
echo Press Ctrl+C to stop viewing logs.
docker compose logs -f
goto end

:clean
echo Cleaning up Docker resources...
echo This will remove all containers, networks, and volumes.
set /p confirm="Are you sure? (y/N): "
if /i "!confirm!"=="y" (
    docker compose down -v --remove-orphans
    docker system prune -f
    echo Cleanup completed.
) else (
    echo Cleanup cancelled.
)
goto end

:restart
echo Restarting all services...
docker compose restart
if %errorlevel% equ 0 (
    echo Services restarted successfully.
) else (
    echo Failed to restart services.
)
goto end

:health
echo Checking health of all services...
echo.
echo Backend:
curl -f http://localhost:8004/health/basic 2>nul && echo " - OK" || echo " - FAILED"
echo.
echo Frontend:
curl -f http://localhost:3000 2>nul && echo " - OK" || echo " - FAILED"
echo.
echo Ollama:
curl -f http://localhost:11434/api/tags 2>nul && echo " - OK" || echo " - FAILED"
echo.
echo Meilisearch:
curl -f http://localhost:7700/version 2>nul && echo " - OK" || echo " - FAILED"
echo.
echo ArangoDB:
curl -f http://localhost:8529/_api/version 2>nul && echo " - OK" || echo " - FAILED"
echo.
echo Qdrant:
curl -f http://localhost:6333/health 2>nul && echo " - OK" || echo " - FAILED"
echo.
echo PostgreSQL:
docker exec sarvanom-postgres pg_isready -U postgres -d sarvanom_db 2>nul && echo " - OK" || echo " - FAILED"
echo.
echo Redis:
docker exec sarvanom-redis redis-cli ping 2>nul && echo " - OK" || echo " - FAILED"
echo.
goto end

:test
echo Running comprehensive Docker health tests...
python test_docker_health.py
goto end

:status
echo Service Status:
docker compose ps
goto end

:end
echo. 