# Run backend without activating venv (works when PowerShell blocks scripts)
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = Join-Path $root "backend\.venv\Scripts\python.exe"

Set-Location (Join-Path $root "backend")
& $py -m alembic upgrade head
& $py seed_user.py
& $py -m uvicorn app.main:app --reload
