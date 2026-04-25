# CloudDash: TUI for Cloudflare - Windows Setup Script

Write-Host "=== CloudDash Setup for Windows ===" -ForegroundColor Cyan

# 1. Create Virtual Environment
Write-Host "`n[1/4] Setting up virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) { 
    Write-Host "Error: Python not found or failed to create venv." -ForegroundColor Red
    exit 
}

# 2. Install Dependencies
Write-Host "[2/4] Installing requirements..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install -q -r requirements.txt

# 3. Interactive Configuration
Write-Host "[3/4] Configuration" -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "Using existing .env file." -ForegroundColor Green
} else {
    Write-Host "Please provide your Cloudflare credentials."
    $token = Read-Host "Enter API Token"
    $acc_id = Read-Host "Enter Account ID"
    
    "CLOUDFLARE_API_TOKEN=$token`nCLOUDFLARE_ACCOUNT_ID=$acc_id" | Out-File -FilePath .env -Encoding utf8
    Write-Host ".env file created successfully!" -ForegroundColor Green
}

# 4. Create Launcher Script (Batch file for easy double-clicking)
Write-Host "[4/4] Creating launcher script (clouddash.bat)..." -ForegroundColor Yellow
$launcherContent = @"
@echo off
set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%venv\Scripts\activate.bat"
python "%SCRIPT_DIR%main.py"
pause
"@
$launcherContent | Out-File -FilePath clouddash.bat -Encoding ascii

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "You can now start CloudDash by double-clicking 'clouddash.bat' or running it in Terminal."
