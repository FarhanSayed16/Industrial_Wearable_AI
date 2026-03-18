@echo off
cd /d "%~dp0..\backend"
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe seed_user.py
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
pause
