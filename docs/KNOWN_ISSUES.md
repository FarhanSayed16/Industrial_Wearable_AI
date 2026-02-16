# Industrial Wearable AI — Known Issues & Fixes

**Purpose:** Record recurring setup problems and their solutions.

---

## Setup Issues

| Issue | Fix |
|-------|-----|
| **PowerShell blocks venv activation** | Option A: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` (run once). Option B: Use `scripts\run-backend.bat` and `scripts\run-edge.bat` (no activation needed). Option C: Use `.\.venv\Scripts\python.exe -m ...` directly. |
| **Port 5432 already in use** | Change docker-compose ports to `"5433:5432"` and use `localhost:5433` in DATABASE_URL |
| **Docker Desktop not running** | Start Docker Desktop; wait for "Docker Engine running" before `docker compose up` |
| **Migrations fail (DB not ready)** | Wait ~10 seconds after `docker compose up -d`; retry `alembic upgrade head` |

---

## Runtime Issues (add as discovered)

| Issue | Fix |
|-------|-----|
| — | — |
