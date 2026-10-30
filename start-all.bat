@echo off
title CareBridge AI Launcher
echo ========================================================
echo   Starting CareBridge AI (Backend + Frontend)
echo ========================================================

echo Starting Backend on http://localhost:8000 ...
start "CareBridge Backend (Port 8000)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Frontend on http://localhost:5173 ...
start "CareBridge Frontend (Port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Done! Both services are starting in separate windows.
echo Frontend URL: http://localhost:5173
echo Backend API : http://localhost:8000/docs
pause

