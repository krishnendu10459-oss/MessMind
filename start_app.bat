@echo off
title AI Food Waste Prediction System
cd /d "%~dp0"

echo ============================================================
echo   AI-POWERED FOOD WASTE PREDICTION SYSTEM
echo   Department of Information Science and Engineering
echo ============================================================
echo.
echo [1/2] Activating Python environment...
call .\venv\Scripts\activate.bat

echo [2/2] Launching Web Browser at http://127.0.0.1:5000 ...
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

echo.
echo ------------------------------------------------------------
echo Server running! Keep this window OPEN while using the app.
echo To STOP the server, press Ctrl+C or close this window.
echo ------------------------------------------------------------
echo.
python run.py

pause
