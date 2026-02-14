# Industrial Wearable AI

AI-driven wearable system for textile manufacturing: real-time activity recognition, risk monitoring, and supervisor dashboard.

## Stack

| Component | Technology |
|-----------|------------|
| Wearable device | ESP32 (IMU, BLE) |
| Edge gateway | Python (laptop) — BLE client, ML inference, API client |
| Backend | FastAPI, PostgreSQL, WebSocket |
| Dashboard | React, TypeScript, Vite |
| ML | scikit-learn, joblib |

**Deployment:** Laptop only (no Raspberry Pi). See `docs/DEPLOYMENT_LAPTOP_ONLY.md`.

## Quick Start

1. **Setup** — Follow `docs/MASTER_PLAN.md` for full implementation guide.
2. **Run** — Follow `docs/RUN_ORDER.md` for step-by-step startup.

```powershell
# 1. Start Postgres
cd backend && docker compose up -d

# 2. Backend
cd backend && .venv\Scripts\Activate.ps1
alembic upgrade head && python seed_user.py
uvicorn app.main:app --reload

# 3. Edge (new terminal)
cd edge && .venv\Scripts\Activate.ps1 && python -m src.main

# 4. Dashboard (new terminal)
cd dashboard && npm run dev

# 5. Open http://localhost:5173 — Login: admin / admin123
```

## Before Pilot

Change the default admin password and set production env vars. See `docs/PILOT_PREP.md`.

```powershell
cd backend && python change_password.py admin
```

## Project Structure

```
├── backend/          # FastAPI, PostgreSQL, WebSocket
├── dashboard/        # React supervisor UI
├── edge/             # BLE client, ML pipeline, API client
├── firmware/         # ESP32 (PlatformIO)
├── ml/               # Training, simulator, data
├── docs/             # Documentation, RESEARCH_PAPER, RUN_COMMANDS
└── docs/uml/         # PlantUML diagrams (use case, component, deployment, sequence, class, activity, state)
```

## Firmware

Replace `firmware/src/main.cpp` with the final ESP32 implementation when hardware is ready. See `firmware/README.md` for build instructions.

## Documentation

- **docs/PROJECT_DOCUMENTATION.md** — **Complete project documentation** (what was built, architecture, features, run, APIs, troubleshooting)
- **docs/RUN_COMMANDS.md** — Commands to run the project (Docker or PostgreSQL on Windows)
- **docs/HARDWARE_CONNECTIONS.md** — Wiring, MPU6050/9250, troubleshooting
- **docs/RUN_ORDER.md** — Service startup order
- **docs/TESTING_WITHOUT_HARDWARE.md** — Test without wearable hardware
- **docs/PILOT_PREP.md** — Pilot deployment checklist
- **docs/TECHNICAL_STACK_SPEC.md** — API contracts, data formats
- **docs/RESEARCH_PAPER.md** — Research paper (problem, solution, methodology, evaluation, references)
