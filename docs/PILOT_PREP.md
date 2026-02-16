# Industrial Wearable AI — Pilot Preparation Checklist

Before deploying for pilot, complete these steps.

## 1. Change Default Admin Password

**Required before any pilot.** The default `admin`/`admin123` must be changed.

```powershell
cd backend
.venv\Scripts\Activate.ps1
python change_password.py admin
# Enter new password when prompted
```

Or with password as argument (avoid for production):

```powershell
python change_password.py admin YourNewSecurePassword
```

## 2. Production Environment Variables

Copy `.env.example` to `.env` in each service and set production values:

### Backend (`backend/.env`)

| Variable | Development | Pilot/Production |
|----------|-------------|------------------|
| DATABASE_URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/wearable_ai` | Same if local; or remote DB URL |
| SECRET_KEY | `change-me-in-production-use-long-random-string` | **Generate a long random string** (e.g. `openssl rand -hex 32`) |
| CORS_ORIGINS | `http://localhost:5173` | Add your dashboard URL(s) |

### Edge (`edge/.env`)

| Variable | Development | Pilot/Production |
|----------|-------------|------------------|
| BACKEND_URL | `http://localhost:8000` | Backend URL (e.g. `http://localhost:8000` or `http://192.168.x.x:8000`) |
| WORKER_ID | `W01` | Unique per device (W01, W02, …) |
| BLE_DEVICE_ID | (empty) | BLE MAC/UUID when using real hardware |

### Dashboard (`dashboard/.env`)

| Variable | Development | Pilot/Production |
|----------|-------------|------------------|
| VITE_API_URL | `http://localhost:8000` | Backend URL |
| VITE_WS_URL | `ws://localhost:8000/ws/live` | WebSocket URL (ws://host:port/ws/live) |

## 3. Test with Multiple Workers (2–5)

Run the simulator with different worker IDs in separate terminals, or use the edge with different `WORKER_ID` values:

```powershell
# Terminal 1
python ml/simulator.py --worker W01 --duration 120 --interval 2

# Terminal 2
python ml/simulator.py --worker W02 --duration 120 --interval 2

# Terminal 3
python ml/simulator.py --worker W03 --duration 120 --interval 2
```

Verify in the dashboard:
- Live View shows all workers
- Alerts panel reflects risk flags
- Shift Summary lists sessions for each worker

## 4. Firmware (When Hardware Ready)

Replace `firmware/src/main.cpp` with the final ESP32 implementation when hardware is available. See `firmware/README.md` for build instructions.

## 5. Run Order

See `docs/RUN_ORDER.md` for step-by-step startup instructions.

## 6. Backup Plan: BLE Failure

If BLE fails during pilot:
- **Edge**: Runs in simulator mode by default when `BLE_DEVICE_ID` is empty
- **Standalone simulator**: Run `python ml/simulator.py` to generate events without edge
- **Wired logging**: Future enhancement; document in KNOWN_ISSUES if needed

## 7. Logging Locations

| Service | Logs |
|--------|------|
| Backend | stdout (uvicorn) |
| Edge | stdout |
| Dashboard | Browser console (F12) |
