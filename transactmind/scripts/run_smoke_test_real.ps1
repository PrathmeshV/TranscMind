# PowerShell helper to run the full smoke test against the real API (requires full dependencies)
param()

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "No virtualenv found at .\.venv. Creating one..."
    python -m venv .venv
}

Write-Host "Activating venv..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing full requirements (this can take several minutes)..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Running full smoke test (real app)..."
python .\tests\smoke_test_real.py

Write-Host "Done."
