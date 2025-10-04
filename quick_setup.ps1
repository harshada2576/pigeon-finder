# quick_setup.ps1 - Fast Setup for Pigeon Finder

Write-Host "🚀 Quick Pigeon Finder Setup" -ForegroundColor Green

# Check if Python 3.12 is available
Write-Host "Checking Python versions..." -ForegroundColor Yellow
$python12 = $false

try {
    $output = & "py" "-3.12" "--version" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $python12 = $true
        Write-Host "✅ Python 3.12 found!" -ForegroundColor Green
    }
} catch {
    Write-Host "Python 3.12 not found, will use available Python" -ForegroundColor Yellow
}

# Remove existing venv
if (Test-Path "venv") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Create virtual environment
if ($python12) {
    Write-Host "Creating virtual environment with Python 3.12..." -ForegroundColor Green
    & "py" "-3.12" "-m" "venv" "venv"
} else {
    Write-Host "Creating virtual environment with available Python..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install packages with pre-compiled wheels
Write-Host "Installing packages..." -ForegroundColor Cyan

$packages = @(
    "customtkinter==5.2.2",
    "Pillow==9.5.0", 
    "psutil==5.9.6",
    "matplotlib==3.8.2", 
    "send2trash==1.8.2",
    "watchdog==3.0.0",
    "PTable==0.9.2"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    & ".\venv\Scripts\python.exe" "-m" "pip" "install" $package
}

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "To run Pigeon Finder:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python run_pigeon_finder.py" -ForegroundColor White

# Test the setup
Write-Host "`nTesting setup..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" "-c" "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
try:
    import customtkinter as ctk
    from PIL import Image
    import psutil
    print('✅ All imports successful!')
    print('🎉 Pigeon Finder is ready!')
except ImportError as e:
    print(f'❌ Import error: {e}')
"