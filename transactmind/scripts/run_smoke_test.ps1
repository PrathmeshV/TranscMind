# PowerShell helper to run the smoke test. Run from repository root (F:\TransacMind\transactmind)
param()

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "No virtualenv found at .\.venv. Creating one..."
    python -m venv .venv
}

Write-Host "Activating venv..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing minimal test deps (fastapi)..."
python -m pip install --upgrade pip
python -m pip install fastapi[all]

Write-Host "Running smoke test..."
python .\tests\smoke_test.py
