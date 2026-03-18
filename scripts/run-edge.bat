@echo off
cd /d "%~dp0..\edge"
.venv\Scripts\python.exe -m src.main
pause
