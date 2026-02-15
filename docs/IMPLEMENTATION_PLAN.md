# Industrial Wearable AI — Complete Implementation Plan

**Document:** Step-by-step implementation guide for the full platform.  
**Version:** 1.0  
**Last updated:** 2025

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Phase 0: Setup & Design](#3-phase-0-setup--design)
4. [Phase 1: Backend](#4-phase-1-backend)
5. [Phase 2: Firmware & Simulator](#5-phase-2-firmware--simulator)
6. [Phase 3: Edge Gateway](#6-phase-3-edge-gateway)
7. [Phase 4: ML Pipeline](#7-phase-4-ml-pipeline)
8. [Phase 5: Dashboard](#8-phase-5-dashboard)
9. [Phase 6: Integration & Pilot](#9-phase-6-integration--pilot)
10. [Timeline & Milestones](#10-timeline--milestones)
11. [Dependencies & Order](#11-dependencies--order)
12. [Quick Start Checklist](#12-quick-start-checklist)

---

## 1. Overview

This document provides a complete, actionable implementation plan for the Industrial Wearable AI platform. The plan follows the architecture defined in `TECHNICAL_STACK_SPEC.md` and the phased approach in `IDEA_AND_APPROACH.md`.

**Core principle:** Build backend-first so Edge and Dashboard can integrate early. Use a data simulator until hardware and ML are ready.

**Target:** End-to-end working system in 4 weeks; pilot-ready in 6 weeks.

---

## 2. Project Structure

```
Industrial_Wearable_AI/
├── firmware/                 # ESP32 wearable firmware
│   ├── src/
│   │   ├── main.cpp
│   │   └── ...
│   ├── platformio.ini
│   └── README.md
│
├── edge/                     # Python edge gateway
│   ├── src/
│   │   ├── main.py
│   │   ├── ble_client.py
│   │   ├── pipeline.py
│   │   ├── feature_extractor.py
│   │   └── classifier.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   │   ├── events.py
│   │   │   ├── workers.py
│   │   │   ├── sessions.py
│   │   │   └── auth.py
│   │   └── services/
│   ├── alembic/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── dashboard/                # React supervisor dashboard
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── api/
│   ├── package.json
│   └── README.md
│
├── ml/                       # ML training & data
│   ├── data/
│   │   ├── raw/              # Raw CSV from ESP32
│   │   ├── labeled/          # Labeled windows
│   │   └── ...
│   ├── models/               # Exported joblib models
│   ├── scripts/
│   │   ├── train.py
│   │   ├── feature_extraction.py
│   │   └── label_tool.py
│   ├── simulator.py          # Mock data generator
│   └── requirements.txt
│
└── docs/                     # Documentation (existing)
```

---

## 3. Phase 0: Setup & Design

**Duration:** 1–2 days  
**Goal:** Project skeleton, schema, API contract.

### 3.1 Tasks

| # | Task | Details |
|---|------|---------|
| 1 | Create directories | `firmware/`, `edge/`, `backend/`, `dashboard/`, `ml/` |
| 2 | Add `.gitignore` | Python, Node, IDE, env files, `__pycache__`, etc. |
| 3 | Database schema | Define tables per `TECHNICAL_STACK_SPEC.md` §3.4 |
| 4 | API contract | Document endpoints, request/response formats |
| 5 | Environment templates | `.env.example` for backend, edge, ml |

### 3.2 Database Schema (Reference)

```sql
-- workers
id (UUID PK), name (VARCHAR), role (VARCHAR), device_id (UUID FK nullable), created_at (TIMESTAMP)

-- devices
id (UUID PK), hardware_id (VARCHAR UNIQUE), worker_id (UUID FK nullable), last_seen_at (TIMESTAMP)

-- sessions
id (UUID PK), worker_id (UUID FK), started_at (TIMESTAMP), ended_at (TIMESTAMP nullable), shift_label (VARCHAR)

-- activity_events
id (UUID PK), session_id (UUID FK), ts (BIGINT), label (ENUM: sewing|idle|adjusting|error|break), risk_ergo (BOOLEAN), risk_fatigue (BOOLEAN)

-- session_aggregates
session_id (UUID PK FK), active_pct (FLOAT), idle_pct (FLOAT), adjusting_pct (FLOAT), error_pct (FLOAT), alert_count (INT), updated_at (TIMESTAMP)
```

**Indexes:** `activity_events(session_id, ts)`, `sessions(worker_id, started_at)`.

### 3.3 API Contract Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/events` | Batch activity events from edge |
| GET | `/api/workers` | List workers |
| GET | `/api/sessions` | List sessions (optional filters) |
| GET | `/api/sessions/{id}/summary` | Session aggregates |
| GET | `/api/live` or WebSocket `/ws/live` | Live worker states |
| POST | `/api/auth/login` | Login → JWT |

### 3.4 Output

- [ ] Project structure created  
- [ ] Schema documented / migrations ready  
- [ ] API contract documented  

---

## 4. Phase 1: Backend

**Duration:** 2–3 days  
**Goal:** FastAPI + PostgreSQL + core endpoints + WebSocket.

### 4.1 Day 1: Project Setup & Database

| # | Task | Details |
|---|------|---------|
| 1 | Create `backend/` | FastAPI project with `app/` structure |
| 2 | `requirements.txt` | fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic, python-jose, passlib[bcrypt], python-dotenv |
| 3 | PostgreSQL | Local install or Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15` |
| 4 | Alembic | Init, create initial migration from schema |
| 5 | Models | SQLAlchemy models for Worker, Device, Session, ActivityEvent, SessionAggregate |
| 6 | Database connection | Async engine, session factory, dependency |

### 4.2 Day 2: Core Endpoints

| # | Task | Details |
|---|------|---------|
| 1 | `POST /api/events` | Accept batch: `{device_id, worker_id, events: [{ts, label, risk_ergo, risk_fatigue}]}`. Validate, insert into `activity_events`. |
| 2 | Aggregation logic | On insert, update or create `session_aggregates` (active_pct, idle_pct, etc.). Compute from event counts. |
| 3 | `GET /api/workers` | Return list of workers with optional device info |
| 4 | `GET /api/sessions` | List sessions, filter by worker_id, date range |
| 5 | `GET /api/sessions/{id}/summary` | Return session aggregates |
| 6 | CORS | Allow dashboard origin |

### 4.3 Day 3: Auth & WebSocket

| # | Task | Details |
|---|------|---------|
| 1 | `POST /api/auth/login` | Username + password → JWT (access token) |
| 2 | Auth dependency | Verify JWT on protected routes |
| 3 | WebSocket `/ws/live` | Accept connections, broadcast `{worker_id, name, current_state, risk_ergo, risk_fatigue, updated_at}` when events arrive |
| 4 | In-memory broadcast | Simple list of WebSocket connections; on POST /events, compute latest state per worker, broadcast to all |

### 4.4 Backend File Checklist

```
backend/
├── app/
│   ├── main.py           # FastAPI app, routes, WebSocket
│   ├── config.py         # Settings from env
│   ├── database.py       # Async engine, session
│   ├── models/
│   │   ├── worker.py
│   │   ├── device.py
│   │   ├── session.py
│   │   ├── activity_event.py
│   │   └── session_aggregate.py
│   ├── schemas/
│   │   ├── events.py     # EventBatch, ActivityEvent
│   │   ├── workers.py
│   │   └── sessions.py
│   └── api/
│       ├── events.py
│       ├── workers.py
│       ├── sessions.py
│       └── auth.py
├── alembic/
├── requirements.txt
└── .env.example
```

### 4.5 Validation

- [ ] `POST /api/events` stores events and updates aggregates  
- [ ] `GET /api/sessions/{id}/summary` returns correct percentages  
- [ ] WebSocket client receives broadcast when events posted  
- [ ] Login returns JWT; protected routes require it  

---

## 5. Phase 2: Firmware & Simulator

**Duration:** 3–5 days (firmware) or 1 day (simulator)  
**Goal:** Data source for development. Simulator first; firmware when hardware ready.

### 5.1 Option A: Data Simulator (Start Here)

**Purpose:** Generate mock IMU-like data and POST to backend. No hardware needed.

| # | Task | Details |
|---|------|---------|
| 1 | Create `ml/simulator.py` | Python script |
| 2 | Generate sequences | Simulate Sewing (rhythmic), Idle (low variance), Adjusting (stop-start) patterns |
| 3 | Output format | Same as wearable: `{worker_id, ts, ax, ay, az, gx, gy, gz, temp}` |
| 4 | POST to backend | Either: (a) POST raw samples to a `/api/raw` endpoint, or (b) simulate edge: classify locally (simple rules) and POST to `/api/events` |
| 5 | Configurable | Worker count, duration, activity mix |

**Simpler approach:** Simulator directly POSTs to `/api/events` with pre-defined labels (Sewing, Idle, etc.) at realistic intervals. No ML needed for initial testing.

### 5.2 Option B: ESP32 Firmware (When Hardware Ready)

| # | Task | Details |
|---|------|---------|
| 1 | PlatformIO project | Create `firmware/` with `platformio.ini` |
| 2 | Libraries | Adafruit_MPU6050, DHT sensor (or OneWire for DS18B20), ArduinoJson, NimBLE or BluetoothSerial |
| 3 | Main loop | Read IMU at 25 Hz, temp at 0.2 Hz; pack JSON; send via BLE |
| 4 | Payload | `{worker_id, ts, ax, ay, az, gx, gy, gz, temp}` |
| 5 | worker_id | Compile-time or NVS |

### 5.3 Simulator Pseudocode

```python
# ml/simulator.py
import requests
import time
import random

ACTIVITIES = ["sewing", "idle", "adjusting", "error", "break"]
BASE_URL = "http://localhost:8000"

def simulate_activity(duration_sec=60, worker_id="W01"):
    events = []
    t = int(time.time() * 1000)
    activity = random.choice(ACTIVITIES)
    for _ in range(duration_sec * 2):  # ~2 events per second
        events.append({"ts": t, "label": activity, "risk_ergo": False, "risk_fatigue": False})
        t += 500
    requests.post(f"{BASE_URL}/api/events", json={"worker_id": worker_id, "events": events})
```

### 5.4 Output

- [ ] Simulator runs and POSTs to backend  
- [ ] Backend receives events; dashboard updates (when built)  
- [ ] (Optional) Firmware streams via BLE  

---

## 6. Phase 3: Edge Gateway

**Duration:** 3–4 days  
**Goal:** BLE → buffer → filter → segment → features → model → POST.

### 6.1 Day 1: BLE & Ingest

| # | Task | Details |
|---|------|---------|
| 1 | Create `edge/` | Python 3.10+ project |
| 2 | `requirements.txt` | bleak, numpy, pandas, scikit-learn, joblib, aiohttp, python-dotenv |
| 3 | BLE client | Use bleak to connect to ESP32; read GATT characteristic; parse JSON |
| 4 | Fallback | If no BLE device, read from simulator script via stdin or local CSV/pipe |
| 5 | Buffer | Append samples to ring buffer (e.g. 5 s at 25 Hz = 125 samples) |

### 6.2 Day 2: Pipeline

| # | Task | Details |
|---|------|---------|
| 1 | Noise filter | Low-pass 5–10 Hz on accel/gyro (scipy or simple moving average) |
| 2 | Sliding window | 2–5 s window, 50% overlap |
| 3 | Feature extraction | Per axis: mean, std, min, max, zero-crossing rate; optional: magnitude |
| 4 | Feature vector | 1D array for model input |

### 6.3 Day 3: Model & POST

| # | Task | Details |
|---|------|---------|
| 1 | Load model | `joblib.load("model.joblib")` at startup |
| 2 | Predict | `model.predict(feature_vector)` → label |
| 3 | Fallback | If no model, use rule-based: low variance → Idle; high rhythmic → Sewing |
| 4 | Rule engine | Optional: idle > 2 min → risk_fatigue; sustained high gyro → risk_ergo |
| 5 | POST | Batch events to `POST /api/events` every N windows or every N seconds |

### 6.4 Day 4: Config & Robustness

| # | Task | Details |
|---|------|---------|
| 1 | `.env` | BACKEND_URL, API_KEY, MODEL_PATH, BLE_DEVICE_IDS |
| 2 | Reconnect logic | If BLE disconnects, retry |
| 3 | Logging | File + console; log level configurable |

### 6.5 Edge File Checklist

```
edge/
├── src/
│   ├── main.py
│   ├── ble_client.py
│   ├── pipeline.py
│   ├── feature_extractor.py
│   ├── classifier.py
│   └── api_client.py
├── requirements.txt
└── .env.example
```

### 6.6 Output

- [ ] Edge connects to wearable (or simulator)  
- [ ] Pipeline produces labels  
- [ ] Events POSTed to backend  
- [ ] Dashboard shows live updates  

---

## 7. Phase 4: ML Pipeline

**Duration:** 3–5 days  
**Goal:** Labeled data → features → train → export model.

### 7.1 Data Collection

| # | Task | Details |
|---|------|---------|
| 1 | Raw data | ESP32 or simulator streams to CSV: `timestamp, ax, ay, az, gx, gy, gz, temp` |
| 2 | Video | Record worker; sync timestamps |
| 3 | Labeling | Tool or manual: assign label per time window (Sewing, Idle, Adjusting, Error, Break) |
| 4 | Output | CSV: `start_ts, end_ts, label` or merged with raw data |
| 5 | Target | 30–60 min labeled data; 500–2000 windows |

### 7.2 Feature Extraction (Same as Edge)

| # | Task | Details |
|---|------|---------|
| 1 | Windows | Sliding 2–5 s, 50% overlap |
| 2 | Features | mean, std, min, max, zero-crossing per axis |
| 3 | Merge | Join with labels; train/val/test split (e.g. 70/15/15) |

### 7.3 Training

| # | Task | Details |
|---|------|---------|
| 1 | Model | RandomForestClassifier or XGBClassifier |
| 2 | Train | Fit on training set |
| 3 | Evaluate | Accuracy, per-class F1; target ≥85% |
| 4 | Export | `joblib.dump(model, "ml/models/activity_model.joblib")` |

### 7.4 Scripts

```
ml/
├── scripts/
│   ├── train.py
│   ├── feature_extraction.py
│   └── label_tool.py (optional)
├── data/
│   ├── raw/
│   └── labeled/
├── models/
│   └── activity_model.joblib
└── requirements.txt
```

### 7.5 Output

- [ ] Labeled dataset created  
- [ ] Model trained, accuracy ≥85%  
- [ ] Model exported; edge loads and uses it  

---

## 8. Phase 5: Dashboard

**Duration:** 3–4 days  
**Goal:** React app with Live view, Alerts, Shift summary.

### 8.1 Day 1: Setup & Auth

| # | Task | Details |
|---|------|---------|
| 1 | Create app | `npm create vite@latest dashboard -- --template react-ts` |
| 2 | Dependencies | react-router-dom, axios, recharts, zustand (or context), react-hot-toast |
| 3 | Login page | Form → POST /api/auth/login → store JWT |
| 4 | Auth context | Provide token; axios interceptor for Authorization header |
| 5 | Protected routes | Redirect to /login if not authenticated |

### 8.2 Day 2: Live View

| # | Task | Details |
|---|------|---------|
| 1 | WebSocket hook | Connect to `/ws/live`; maintain worker state in state store |
| 2 | Worker cards | List workers; each card: name, current_state badge, risk_ergo, risk_fatigue |
| 3 | Fallback | If WebSocket fails, poll GET /api/live or /api/workers every 2–5 s |
| 4 | Styling | MUI or Chakra or Tailwind; clear badges for state and risk |

### 8.3 Day 3: Alerts & Shift Summary

| # | Task | Details |
|---|------|---------|
| 1 | Alerts panel | List recent alerts (ergo/fatigue) with worker, time |
| 2 | Shift summary | Table or bar chart: active_pct, idle_pct per worker for selected session |
| 3 | Session selector | Dropdown or date picker to choose session |
| 4 | API | GET /api/sessions, GET /api/sessions/{id}/summary |

### 8.4 Day 4: Polish

| # | Task | Details |
|---|------|---------|
| 1 | Toasts | react-hot-toast for real-time alerts |
| 2 | Routing | `/` (live), `/sessions`, `/workers`, `/login` |
| 3 | Responsive | Basic mobile-friendly layout |

### 8.5 Dashboard File Checklist

```
dashboard/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── api/
│   │   ├── client.ts
│   │   └── auth.ts
│   ├── components/
│   │   ├── WorkerCard.tsx
│   │   ├── AlertsPanel.tsx
│   │   └── ShiftSummary.tsx
│   ├── pages/
│   │   ├── LiveView.tsx
│   │   ├── Sessions.tsx
│   │   └── Login.tsx
│   └── hooks/
│       └── useWebSocket.ts
├── package.json
└── .env
```

### 8.6 Output

- [ ] Login works  
- [ ] Live view shows workers with state and risk  
- [ ] Alerts panel shows recent alerts  
- [ ] Shift summary shows active % per worker  

---

## 9. Phase 6: Integration & Pilot

**Duration:** 1–2 weeks  
**Goal:** End-to-end stable; pilot in real environment.

### 9.1 Integration Tasks

| # | Task | Details |
|---|------|---------|
| 1 | End-to-end test | Wearable (or simulator) → Edge → Backend → Dashboard |
| 2 | Latency | Motion to dashboard < 5 s |
| 3 | Stability | 8-hour run without crashes |
| 4 | BLE | Test range, reconnect; one gateway per room if needed |
| 5 | Thresholds | Tune ergo/fatigue rules to reduce false positives |

### 9.2 Pilot Prep

| # | Task | Details |
|---|------|---------|
| 1 | Deploy | Edge + backend on laptop; dashboard on same machine |
| 2 | Workers | 2–5 workers; assign devices; brief on purpose |
| 3 | Duration | 1–2 weeks, one shift per day |
| 4 | Feedback | Supervisor survey: "Useful?" "What's missing?" |
| 5 | Report | Accuracy in field, satisfaction, testimonial |

### 9.3 Output

- [ ] Pilot completed  
- [ ] Supervisor can answer "who is idle?" in < 30 s  
- [ ] One testimonial or letter of interest  

---

## 10. Timeline & Milestones

| Week | Focus | Milestone |
|------|--------|-----------|
| **1** | Backend + Simulator + Dashboard scaffold | Backend accepts events; simulator feeds it; dashboard shows live state |
| **2** | Edge + ML | Edge runs pipeline; ML model trained; end-to-end with simulator |
| **3** | Firmware (optional) + Polish | ESP32 streams to edge; or continue with simulator; bug fixes |
| **4** | Integration | Full stack stable; ready for pilot |
| **5–6** | Pilot | Deploy; 2–5 workers; collect feedback |

### Key Milestones

| Milestone | Description |
|-----------|-------------|
| **M1** | Backend + DB + POST /events + aggregates working |
| **M2** | Simulator POSTs; dashboard shows live updates |
| **M3** | Edge pipeline runs; labels POSTed to backend |
| **M4** | ML model trained; edge uses it |
| **M5** | End-to-end: wearable/simulator → edge → backend → dashboard |
| **M6** | Pilot complete; supervisor says "useful" |

---

## 11. Dependencies & Order

```
                    ┌─────────────┐
                    │   Phase 0   │
                    │ Setup       │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Phase 1   │
                    │ Backend     │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
    │ Phase 2 │      │  Phase 3   │    │ Phase 5   │
    │ Simulator│     │ Edge       │    │ Dashboard │
    └────┬────┘      └─────┬─────┘    └─────┬─────┘
         │                 │                 │
         │            ┌────▼────┐            │
         │            │ Phase 4 │            │
         │            │ ML      │            │
         │            └────┬────┘            │
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Phase 6   │
                    │ Integration │
                    └─────────────┘
```

**Critical path:** Phase 0 → Phase 1 → Phase 2 (simulator) + Phase 5 (dashboard) can run in parallel. Phase 3 (edge) needs Phase 1. Phase 4 (ML) can run in parallel; edge uses model when ready.

---

## 12. Quick Start Checklist

### Day 1

- [ ] Create `backend/`, `edge/`, `dashboard/`, `ml/` directories  
- [ ] Set up backend: FastAPI, PostgreSQL, Alembic  
- [ ] Create database schema and run migrations  
- [ ] Implement `POST /api/events` and aggregation  
- [ ] Test with curl/Postman  

### Day 2

- [ ] Implement `GET /api/workers`, `GET /api/sessions`, `GET /api/sessions/{id}/summary`  
- [ ] Create `ml/simulator.py` — POST mock events to backend  
- [ ] Implement WebSocket `/ws/live`  
- [ ] Verify simulator → backend → WebSocket broadcast  

### Day 3

- [ ] Implement `POST /api/auth/login`  
- [ ] Create React dashboard project  
- [ ] Login page + auth flow  
- [ ] WebSocket hook + Live view with worker cards  

### Day 4

- [ ] Dashboard: Alerts panel, Shift summary  
- [ ] Polish UI; test full flow: simulator → backend → dashboard  

### Day 5

- [ ] Start edge gateway: BLE client or simulator input  
- [ ] Pipeline: filter, segment, feature extraction  
- [ ] (If no model) Rule-based labels; POST to backend  
- [ ] End-to-end: edge → backend → dashboard  

### Week 2+

- [ ] ML: collect/label data, train model, export  
- [ ] Edge loads model; replace rule-based with ML  
- [ ] Firmware (if hardware ready)  
- [ ] Integration testing, pilot prep  

---

## Appendix A: Environment Variables

### Backend (`.env`)

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/wearable_ai
SECRET_KEY=your-jwt-secret
CORS_ORIGINS=http://localhost:5173
```

### Edge (`.env`)

```
BACKEND_URL=http://localhost:8000
API_KEY=optional-edge-api-key
MODEL_PATH=../ml/models/activity_model.joblib
BLE_DEVICE_IDS=AA:BB:CC:DD:EE:FF
WINDOW_SECONDS=3
OVERLAP=0.5
```

### Dashboard (`.env`)

```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/live
```

---

## Appendix B: API Request/Response Examples

### POST /api/events

**Request:**
```json
{
  "device_id": "ESP32_ABC123",
  "worker_id": "W01",
  "events": [
    { "ts": 1704067200123, "label": "sewing", "risk_ergo": false, "risk_fatigue": false },
    { "ts": 1704067202123, "label": "idle", "risk_ergo": false, "risk_fatigue": true }
  ]
}
```

- **label:** one of `sewing`, `idle`, `adjusting`, `error`, `break`
- **ts:** Unix milliseconds

### WebSocket /ws/live (message to client)

```json
{
  "worker_id": "W01",
  "name": "Operator 1",
  "current_state": "idle",
  "risk_ergo": false,
  "risk_fatigue": true,
  "updated_at": 1704067202123
}
```

---

*This document is the implementation guide. Refer to `TECHNICAL_STACK_SPEC.md` for technical details and `IDEA_AND_APPROACH.md` for product strategy.*
