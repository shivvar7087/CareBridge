# Start CareBridge AI Backend
Write-Host "Starting CareBridge AI FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

