@echo off
echo ============================================================================
echo Docker Desktop Service Check
echo ============================================================================
echo.

echo Checking Docker services...
sc query "com.docker.service" >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Docker service
    sc query "com.docker.service"
) else (
    echo Docker service not found
)

echo.
echo Checking Docker Desktop service...
sc query "Docker Desktop Service" >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Docker Desktop service
    sc query "Docker Desktop Service"
) else (
    echo Docker Desktop service not found
)

echo.
echo Checking if Docker Desktop is running...
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>NUL | find /I /N "Docker Desktop.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Docker Desktop process is running
) else (
    echo Docker Desktop process is NOT running
)

echo.
echo Checking Docker CLI access...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker CLI is accessible
) else (
    echo Docker CLI is NOT accessible
)

echo.
echo ============================================================================
echo Troubleshooting Steps:
echo ============================================================================
echo.
echo 1. Restart Docker Desktop completely:
echo    - Right-click Docker Desktop icon in system tray
echo    - Select "Quit Docker Desktop"
echo    - Wait 30 seconds
echo    - Start Docker Desktop from Start Menu
echo    - Wait 3-5 minutes for full initialization
echo.
echo 2. If still having issues:
echo    - Open Docker Desktop
echo    - Go to Settings (gear icon)
echo    - Check "Use the WSL 2 based engine"
echo    - Apply and Restart
echo.
echo 3. Alternative: Reset Docker Desktop:
echo    - Open Docker Desktop
echo    - Go to Settings
echo    - Click "Reset to factory defaults"
echo    - Restart Docker Desktop
echo.
echo 4. Check Windows Defender/Firewall:
echo    - Make sure Docker Desktop is allowed
echo    - Temporarily disable antivirus if needed
echo.
pause 