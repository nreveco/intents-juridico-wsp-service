@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0docker-rebuild.ps1" %*

endlocal
