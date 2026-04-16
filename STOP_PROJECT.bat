@echo off
echo [STOP] Shutting down MEC containers ...
cd /D "%~dp0"
docker-compose down
echo [OK] All containers stopped.
pause
