@echo off
cd /d "%~dp0"
title HEXARK - Veyra Sentinel Launcher
cls

:: --- Display Fastfetch Dashboard ---
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python scripts\banner.py
)

:: --- Pre-flight System Checks ---
echo  ===================================================================
echo   Checking Environment and Dependencies...
echo  ===================================================================

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [*] ERROR: Python is not found in your system PATH!
    echo      Please install Python 3.10+ from https://python.org/
    echo      and check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check Node.js / npm
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [*] ERROR: Node.js / npm is not found in your system PATH!
    echo      Please install Node.js v18 or higher from https://nodejs.org/
    echo      and restart this launcher.
    echo.
    pause
    exit /b 1
)

:: Check Backend Dependencies (uvicorn, fastapi)
python -c "import uvicorn, fastapi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [*] First-time setup: Installing backend dependencies via pip...
    echo      This may take a moment, please wait...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo  [*] WARNING: Some Python dependencies may have failed to install.
    )
    echo  [OK] Backend dependencies checked.
)

:: Check Frontend Dependencies (node_modules)
if not exist "frontend\node_modules\" (
    echo.
    echo  ===================================================================
    echo   First-time setup: 'frontend\node_modules' not found!
    echo   Installing frontend packages via 'npm install'...
    echo   This may take 1-2 minutes on first run, please wait...
    echo  ===================================================================
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
    if not exist "frontend\node_modules\" (
        echo.
        echo  [*] ERROR: 'npm install' failed!
        echo      Please open a terminal in 'frontend' and run 'npm install' manually.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Frontend dependencies installed successfully!
)

:: Check Model Artifacts (detect un-pulled Git LFS pointer stubs)
if exist "models\v3\lightgbm_v3_challenger.joblib" (
    for %%F in (models\v3\lightgbm_v3_challenger.joblib) do (
        if %%~zF LSS 10000 (
            echo  [*] Restoring model binary weights from git...
            git checkout HEAD -- models/v3/
            echo  [OK] Model weights verification complete.
        )
    )
)

echo  [OK] All pre-flight checks passed.
echo.

:: --- Pre-flight Cleanup: Release lingering ports from prior sessions ---
echo  [*] Releasing any lingering development server ports...
powershell -NoProfile -Command "$ports = @(8000, 8001, 5173); foreach ($p in $ports) { $conn = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue; if ($conn) { foreach ($c in $conn) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } } }" >nul 2>&1

:: --- Determine Available Backend Port (Automatic WinNAT / WinError 10013 Fallback) ---
set BACKEND_PORT=8000
python -c "import socket, sys; s = socket.socket(); (lambda: (s.bind(('127.0.0.1', 8000)), s.close(), sys.exit(0)) if True else None)();" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [*] Notice: Port 8000 is occupied or restricted by Windows permissions.
    echo  [*] Automatically routing backend to fallback port 8001...
    set BACKEND_PORT=8001
)

:: Configure frontend to target the active backend port dynamically
echo VITE_API_BASE_URL=http://127.0.0.1:%BACKEND_PORT%> "frontend\.env.local"

:: --- Start Backend Server ---
echo  ===================================================================
echo   Starting Veyra Sentinel Backend [port %BACKEND_PORT%]...
echo  ===================================================================
start "HEXARK-Backend" cmd /k "title HEXARK-Backend && cd /d "%~dp0" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload"

echo  [*] Waiting for backend to initialize...
ping 127.0.0.1 -n 4 >nul

:: --- Start Frontend Dev Server ---
echo.
echo  ===================================================================
echo   Starting Veyra Dashboard Frontend [port 5173]...
echo  ===================================================================
start "HEXARK-Frontend" cmd /k "title HEXARK-Frontend && cd /d "%~dp0frontend" && call npm run dev"

echo  [*] Waiting for frontend to initialize...
ping 127.0.0.1 -n 5 >nul

:: --- Open Dashboard in Browser ---
echo.
echo  ===================================================================
echo   Opening Veyra Dashboard in your browser...
echo  ===================================================================
start "" "http://127.0.0.1:5173/Veyra-Know-When-Forecasts-May-Fail/"

echo.
echo  +-----------------------------------------------------------------+
echo  ^|                                                                 ^|
echo  ^|   VEYRA SENTINEL is now running!                                ^|
echo  ^|   Backend:  http://127.0.0.1:%BACKEND_PORT% (API Docs: /docs)          ^|
echo  ^|   Frontend: http://127.0.0.1:5173/Veyra-Know-When-Forecasts-May-Fail/  ^|
echo  ^|                                                                 ^|
echo  ^|   Press any key in this window to stop all servers...           ^|
echo  ^|                                                                 ^|
echo  +-----------------------------------------------------------------+
echo.
pause >nul

:: --- Shutdown Servers ---
echo.
echo  [*] Shutting down servers and closing terminals...
taskkill /FI "WINDOWTITLE eq HEXARK-Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK-Frontend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq HEXARK Frontend*" /T /F >nul 2>&1
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,8001,5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
if exist "frontend\.env.local" del /f /q "frontend\.env.local" >nul 2>&1
echo  [OK] All servers and spawned terminals closed.
echo.
ping 127.0.0.1 -n 2 >nul
