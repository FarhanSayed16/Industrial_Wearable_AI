# Testing Without Hardware

**How to test the full project end-to-end when no ESP32/wearable is connected.**

The system uses **simulator mode** instead of real BLE — no hardware required.

---

## Fix PowerShell First (Required on Windows)

If you see *"running scripts is disabled on this system"* when activating the venv:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Run this **once** in PowerShell as Administrator (or CurrentUser works without admin). Then restart PowerShell.

**Alternative (no execution policy change):**
- Use the included **run scripts**: `scripts\run-backend.bat` and `scripts\run-edge.bat` (double-click or run from cmd)
- Or use the venv's Python directly — see [Commands Without Activation](#commands-without-activation) below.

---

## Prerequisites

| Item | Check |
|------|-------|
| Docker | Running (for PostgreSQL) |
| Python 3.10+ | `python --version` |
| Node.js 18+ | `node --version` |
| Virtual environments | `.venv` in `backend/`, `edge/`, `ml/` |

If venvs are missing:

```powershell
cd backend; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt
cd edge; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt
cd ml; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt
cd dashboard; npm install
```

---

## Quick Test (5 Minutes)

### Step 1: Start PostgreSQL

```powershell
cd D:\Industrial_Wearable_AI\backend
docker compose up -d
docker compose ps
```

Wait ~5 seconds for Postgres to be ready.

### Step 2: Start Backend

**New terminal (Terminal 1):**

```powershell
cd D:\Industrial_Wearable_AI\backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python seed_user.py
uvicorn app.main:app --reload
```

Leave running. You should see `Uvicorn running on http://127.0.0.1:8000`.

### Step 3: Start Edge (Simulator Mode)

**New terminal (Terminal 2):**

```powershell
cd D:\Industrial_Wearable_AI\edge
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main
```

Leave running. You should see `Model loaded from ...` or `No model; using rule-based classifier`, then samples being processed.

**No BLE device needed** — edge uses built-in simulator when `BLE_DEVICE_ID` is empty.

### Step 4: Start Dashboard

**New terminal (Terminal 3):**

```powershell
cd D:\Industrial_Wearable_AI\dashboard
npm run dev
```

Leave running. Note the URL (e.g. `http://localhost:5173`).

### Step 5: Open Dashboard and Verify

1. Open **http://localhost:5173** in a browser
2. Login: `admin` / `admin123`
3. You should see **Live View** with worker cards updating (e.g. W01)
4. Check **Connected** badge (green)
5. Go to **Shift Summary** → `/sessions` — sessions should appear
6. Select a session — summary (active_pct, idle_pct, etc.) should show

### Step 6: (Optional) Add More Workers

**New terminal (Terminal 4):**

```powershell
cd D:\Industrial_Wearable_AI\ml
.venv\Scripts\Activate.ps1
python simulator.py --worker W02 --duration 60 --interval 2
```

This runs the standalone simulator for 60 seconds. Worker W02 will appear in Live View.

---

## What to Verify

| Test | Expected Result |
|------|-----------------|
| Backend | http://localhost:8000/docs loads; `GET /api/version` returns JSON |
| Login | `admin` / `admin123` works |
| Live View | Worker cards appear and update; status shows sewing/idle/adjusting |
| WebSocket | Green "Connected" badge |
| Alerts | When risk flags are set, alerts panel shows worker |
| Shift Summary | Sessions list loads; selecting a session shows percentages |
| Filters | State filter (idle, sewing) and risk filter work |

---

## Verification Commands (Optional)

Run these in a separate terminal to verify APIs:

```powershell
# Backend health
Invoke-RestMethod -Uri http://localhost:8000/api/version

# Login and get workers (PowerShell)
$body = '{"username":"admin","password":"admin123"}'
$login = Invoke-RestMethod -Uri http://localhost:8000/api/auth/login -Method POST -ContentType "application/json" -Body $body
$token = $login.access_token
Invoke-RestMethod -Uri http://localhost:8000/api/workers -Headers @{Authorization="Bearer $token"}
```

---

## Shutdown

1. Stop edge (Ctrl+C in Terminal 2)
2. Stop simulator if running (Ctrl+C in Terminal 4)
3. Stop dashboard (Ctrl+C in Terminal 3)
4. Stop backend (Ctrl+C in Terminal 1)
5. Stop Postgres: `cd backend; docker compose down`

---

## Commands Without Activation

If PowerShell blocks `Activate.ps1`, use the venv's Python directly:

**Backend:**
```powershell
cd D:\Industrial_Wearable_AI\backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe seed_user.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

**Edge:**
```powershell
cd D:\Industrial_Wearable_AI\edge
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
```

**Simulator:**
```powershell
cd D:\Industrial_Wearable_AI
.\ml\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\ml\.venv\Scripts\python.exe ml/simulator.py --worker W02 --duration 60 --interval 2
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **PowerShell blocks venv** | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` or use [Commands Without Activation](#commands-without-activation) |
| **alembic/uvicorn not found** | Activate venv first, or use `.\.venv\Scripts\python.exe -m alembic` etc. |
| **ModuleNotFoundError (bcrypt, dotenv)** | Run `pip install -r requirements.txt` inside the correct venv |
| **`docker compose` fails** | Start Docker Desktop; wait for "Docker Engine running" |
| **Backend: connection refused to DB** | Wait 10s after `docker compose up`; retry |
| **No workers in Live View** | Ensure edge is running (Terminal 2); check WebSocket badge is green |
| **Login fails** | Run `python seed_user.py` (with backend venv active) |
| **Port 8000 or 5173 in use** | Stop other apps using those ports |

---

## Summary

| Component | Role (No Hardware) |
|-----------|-------------------|
| **Edge** | Simulates IMU samples internally; runs ML; POSTs to backend |
| **Simulator** | Optional; generates events directly to backend |
| **Dashboard** | Same as with hardware — real-time updates via WebSocket |

You can test the full pipeline (data → ML → backend → dashboard) without any wearable hardware.
