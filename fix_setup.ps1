# fix_setup.ps1 - Fix Python Version Issues

Write-Host "Fixing Pigeon Finder Setup..." -ForegroundColor Green

# Check available Python versions
Write-Host "Checking Python versions..." -ForegroundColor Yellow
py -0

Write-Host "`nPlease use Python 3.11 or 3.12 for compatibility." -ForegroundColor Cyan
Write-Host "Python 3.13 is too new and doesn't have pre-compiled packages yet." -ForegroundColor Red

# Remove existing venv
if (Test-Path "venv") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Try Python 3.11 first, then 3.12
$python_versions = @("3.11", "3.12", "3.10", "3.9")

foreach ($version in $python_versions) {
    Write-Host "`nTrying Python $version..." -ForegroundColor Cyan
    try {
        $output = & "py" "-$version" "-c" "print('Python $version available')" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Found Python $version! Setting up..." -ForegroundColor Green
            
            # Create virtual environment
            & "py" "-$version" "-m" "venv" "venv"
            
            # Activate and install
            & ".\venv\Scripts\Activate.ps1"
            & ".\venv\Scripts\python.exe" "-m" "pip" "install" "--upgrade" "pip"
            
            # Install packages
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
            
            Write-Host "`n✅ Setup successful with Python $version!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "Python $version not available" -ForegroundColor Yellow
    }
}

Write-Host "`nTo run Pigeon Finder:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor White