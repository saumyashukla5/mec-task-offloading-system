@echo off
REM ═══════════════════════════════════════════════════════════════
REM  MEC Emulation – Windows Launcher
REM  Run this file from the mec_emulation\ root folder
REM ═══════════════════════════════════════════════════════════════

SETLOCAL ENABLEDELAYEDEXPANSION
SET ROOT=%~dp0

echo.
echo ╔══════════════════════════════════════════╗
echo ║   MEC EMULATION PROJECT – LAUNCHER       ║
echo ╚══════════════════════════════════════════╝
echo.

REM ── Step 1: Check Docker is running ────────────────────────
docker info >NUL 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Docker Desktop is NOT running.
    echo         Please start Docker Desktop and try again.
    pause
    EXIT /B 1
)
echo [OK] Docker Desktop is running.

REM ── Step 2: Check Python is installed ──────────────────────
python --version >NUL 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python 3 is not installed or not on PATH.
    pause
    EXIT /B 1
)
echo [OK] Python found.

REM ── Step 3: Install orchestrator dependencies ───────────────
echo.
echo [SETUP] Installing Python dependencies for orchestrator ...
pip install -r "%ROOT%client_orchestrator\requirements.txt" --quiet
echo [OK] Dependencies installed.

REM ── Step 4: Build and start Docker containers ───────────────
echo.
echo [DOCKER] Building and starting Edge + Cloud servers ...
cd /D "%ROOT%"
docker-compose up --build -d

IF ERRORLEVEL 1 (
    echo [ERROR] docker-compose failed. Check Docker Desktop is running.
    pause
    EXIT /B 1
)
echo [OK] Containers started.

REM ── Step 5: Wait a moment for containers to be ready ────────
echo.
echo [WAIT] Giving servers 5 seconds to initialise ...
timeout /t 5 /nobreak >NUL

REM ── Step 6: Run the orchestrator ────────────────────────────
echo.
echo [RUN] Starting MEC Orchestrator ...
python "%ROOT%client_orchestrator\orchestrator.py"

REM ── Step 7: Done ────────────────────────────────────────────
echo.
echo [DONE] Results saved in: %ROOT%results\
echo        Open the PNG files to view your graphs.
echo.

REM Optional: open results folder
explorer "%ROOT%results"

pause
