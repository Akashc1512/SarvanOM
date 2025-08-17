#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SarvanOM Development Environment Check Script (PowerShell)

.DESCRIPTION
    This script verifies the development environment is properly configured:
    - Python ≥3.11
    - Node ≥18
    - Docker present
    - Required environment variables in .env, .env.docker, frontend/.env.local

.PARAMETER Help
    Show this help message

.EXAMPLE
    .\scripts\dev_check.ps1

.EXAMPLE
    python scripts\dev_check.py
#>

param(
    [switch]$Help
)

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

Write-Host "SarvanOM Development Environment Check (PowerShell)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python is available: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python not found" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Node.js is available: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Node.js not found" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
}

# Check if Docker is available
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker is available: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker not found or not running" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Docker not found or not running" -ForegroundColor Red
}

Write-Host ""
Write-Host "Running comprehensive environment check..." -ForegroundColor Yellow

# Run the Python script
try {
    python scripts\dev_check.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Environment check completed successfully" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ Environment check failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "✗ Failed to run environment check: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Alternative commands:" -ForegroundColor Cyan
Write-Host "  python scripts\dev_check.py    # Direct Python execution" -ForegroundColor White
Write-Host "  .\scripts\dev_check.ps1        # PowerShell wrapper" -ForegroundColor White
Write-Host "  make doctor                    # Make command (if available)" -ForegroundColor White
