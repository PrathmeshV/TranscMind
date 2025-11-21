# Recreate a clean venv and upgrade pip
# Run this in PowerShell (may need to run as Administrator if permissions issues persist)
param()

$venvPath = Join-Path -Path $PWD -ChildPath '.venv'
if (Test-Path $venvPath) {
    Write-Host "Removing existing venv at $venvPath ..."
    try {
        Remove-Item -Recurse -Force $venvPath
    }
    catch {
        Write-Host "Failed to remove .venv: $_.Exception.Message"
        Write-Host "Try closing other terminals or running PowerShell as Administrator. Exiting."
        exit 1
    }
}

Write-Host "Creating venv..."
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create venv. Ensure Python is on PATH and you have permissions."
    exit 1
}

Write-Host "Activating venv and upgrading pip..."
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip upgrade failed. Try running PowerShell as Administrator or close software that may lock files (antivirus)."
    exit 1
}

Write-Host "Virtual environment ready. Activate with: .\\.venv\\Scripts\\Activate.ps1"
