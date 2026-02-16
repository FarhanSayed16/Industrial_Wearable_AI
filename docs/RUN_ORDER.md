# Industrial Wearable AI — Run Order

Step-by-step instructions to start all services for integration testing and pilot.

## Before Pilot

**Before deploying for pilot:** Change the default admin password and set production env vars. See `docs/PILOT_PREP.md`.

```powershell
cd backend
python change_password.py admin
```

## Prerequisites

- Python 3.10+ with venv per service (backend, edge, ml)
- Node.js 18+ for dashboard
- Docker (for PostgreSQL)
- PowerShell or terminal

## 1. Start PostgreSQL

```powershell
cd backend
docker compose up -d
docker compose ps   # verify postgres is running
```

Wait a few seconds for Postgres to be ready. Check logs if needed:

```powershell
docker compose logs -f postgres
```

## 2. Start Backend

```powershell
cd backend
.venv\Scripts\Activate.ps1   # or: source .venv/bin/activate on Unix
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000. API docs: http://localhost:8000/docs

**First run:** Ensure migrations are applied, admin user is seeded, and (optional) demo workers with 45-day history for showcase:

```powershell
alembic upgrade head
python seed_user.py
python seed_demo_workers.py   # optional: adds W01–W08, 45 days history for W02–W08
```

## 3. Start Edge Gateway

In a **new terminal**:

```powershell
cd edge
.venv\Scripts\Activate.ps1
python -m src.main
```

Edge uses simulator mode by default (no BLE device). It posts events to the backend.

## 4. Start Dashboard

In a **new terminal**:

```powershell
cd dashboard
npm run dev
```

Dashboard runs at http://localhost:5173 (or the port Vite shows).

## 5. (Optional) Run Simulator

If not using the edge, run the standalone simulator to generate events:

```powershell
cd ml
.venv\Scripts\Activate.ps1
python simulator.py --worker W01 --duration 60 --interval 2
```

## 6. Open Dashboard

1. Open http://localhost:5173 in a browser
2. Login: `admin` / `admin123`
3. Live View: worker cards should update as edge/simulator posts events
4. Shift Summary: go to /sessions to see session list and summaries

## Shutdown Order

1. Stop simulator (Ctrl+C) if running
2. Stop edge (Ctrl+C)
3. Stop dashboard (Ctrl+C)
4. Stop backend (Ctrl+C)
5. Stop Postgres: `cd backend && docker compose down`

## Troubleshooting

| Issue | Check |
|-------|-------|
| Backend won't start | Postgres running? `DB_URL` in backend/.env correct? |
| No events in dashboard | Edge or simulator running? WebSocket connected (green badge)? |
| Login fails | Run `python backend/seed_user.py` |
| Pilot: change password | Run `python backend/change_password.py admin` |
| Port in use | Change ports in .env or stop conflicting process |
