# End-to-End Test Runner for PowerShell
# This script runs comprehensive E2E tests for the real backend pipeline

param(
    [switch]$Verbose,
    [string]$SpecificTest,
    [switch]$HealthOnly,
    [switch]$ReportOnly
)

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Real Backend Pipeline E2E Test Runner" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the project root
if (-not (Test-Path "services")) {
    Write-Host "❌ ERROR: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Expected to find 'services' directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if test file exists
if (-not (Test-Path "tests\e2e\test_real_backend_pipeline.py")) {
    Write-Host "❌ ERROR: Test file not found" -ForegroundColor Red
    Write-Host "Expected: tests\e2e\test_real_backend_pipeline.py" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔧 Checking environment..." -ForegroundColor Blue
Write-Host ""

# Check if required packages are installed
$packages = @("pytest", "httpx", "pytest-asyncio")

foreach ($package in $packages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "✅ $package is available" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Installing $package..." -ForegroundColor Yellow
        pip install $package
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install $package" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

Write-Host ""
Write-Host "🚀 Running E2E tests..." -ForegroundColor Blue
Write-Host ""

# Build command arguments
$args = @()

if ($Verbose) {
    $args += "--verbose"
}

if ($SpecificTest) {
    $args += "--specific-test"
    $args += $SpecificTest
}

if ($HealthOnly) {
    $args += "--health-only"
}

if ($ReportOnly) {
    $args += "--report-only"
}

# Run the test runner script
$startTime = Get-Date
$result = python run_e2e_tests.py @args
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "   Tests completed with errors" -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Check if all services are running" -ForegroundColor White
    Write-Host "2. Verify environment variables are set" -ForegroundColor White
    Write-Host "3. Check the test logs above for specific errors" -ForegroundColor White
    Write-Host "4. Run with -Verbose flag for more details" -ForegroundColor White
    Write-Host ""
    Write-Host "Command: .\run_e2e_tests.ps1 -Verbose" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "   All tests completed successfully!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Duration: $([math]::Round($duration, 2)) seconds" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Review test results and performance metrics" -ForegroundColor White
    Write-Host "2. Validate response quality manually" -ForegroundColor White
    Write-Host "3. Monitor system resources" -ForegroundColor White
    Write-Host "4. Update documentation if needed" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press Enter to exit..."
Read-Host 