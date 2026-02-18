# Industrial Wearable AI — Master Plan (Step-by-Step Implementation Guide)

**Document:** Single source of truth for full project implementation.  
**Purpose:** Follow steps and file specifications — implement code as per your requirements at implementation time.  
**Deployment:** Laptop only (no Raspberry Pi).  
**Version:** 2.0  
**Last updated:** 2025-02-04

---

## Implementation Status

| Phase | Status | Notes |
|-------|--------|-------|
| 1 | ✅ Complete | All directories, .gitignore, DECISIONS.md, KNOWN_ISSUES.md |
| 2 | ✅ Complete | Backend DB, models, Alembic, Docker Postgres |
| 101 | ✅ Complete | Checkpoint Gate A passed |
| 3 | ✅ Complete | API endpoints: POST /events, GET /workers, GET /sessions, GET /sessions/{id}/summary |
| 4 | ✅ Complete | Auth (JWT login), WebSocket /ws/live, seed admin |
| 102 | ✅ Complete | Checkpoint Gate B passed |
| 5 | ✅ Complete | Data simulator (ml/simulator.py) |
| 6 | ✅ Complete | Firmware structure (platformio.ini, placeholder main.cpp, README) |
| 7 | ✅ Complete | Edge BLE client (simulator), sample buffer |
| 8 | ✅ Complete | Edge pipeline (feature extractor, low-pass, process_window) |
| 9 | ✅ Complete | Edge classifier, API client, main (samples→label→POST) |
| 10 | ✅ Complete | ML data collection (collect_raw, validate_raw_csv, labeling README) |
| 11 | ✅ Complete | ML training (train.py, feature extraction, RandomForest, joblib export) |
| 12 | ✅ Complete | ML/Edge integration (model loads, end-to-end predictions) |
| 13 | ✅ Complete | Dashboard setup (React, Vite, login, auth, routing) |
| 14 | ✅ Complete | Live View (useWebSocket, worker cards, connection status) |
| 15 | ✅ Complete | Alerts panel, sessions API, Shift Summary page |
| 106 | ✅ Complete | Checkpoint Gate F passed (UX, reconnect, filters, last updated) |
| 16 | ✅ Complete | Integration verified; RUN_ORDER.md created |
| 17 | ✅ Complete | Pilot prep: change_password, PILOT_PREP.md, multi-worker test |
| 18 | ✅ Complete | README.md, docs updated |
| 107 | ✅ Complete | Checkpoint Gate G passed — pilot ready |

---

## How to Use This Document

1. **Work in order** — Phases 1–18 must be done sequentially.
2. **For each file:** Follow the **Steps**, implement the **Features**, meet the **Requirements**.
3. **Code:** Write code at implementation time based on these specs; do not copy outdated code.
4. **Reference docs:** Use `TECHNICAL_STACK_SPEC.md` for data formats, API contracts, schema.
5. **Check off** each step and verification as you complete it.

---

## Table of Contents

| Phase | Title |
|-------|-------|
| 1 | [Project Setup & Structure](#phase-1-project-setup--structure) |
| 2 | [Backend — Database & Models](#phase-2-backend--database--models) |
| 101 | [Checkpoint Gate A — Backend DB & Migrations Audit](#phase-101-checkpoint-gate-a--backend-db--migrations-audit) |
| 3 | [Backend — API Endpoints](#phase-3-backend--api-endpoints) |
| 4 | [Backend — Auth & WebSocket](#phase-4-backend--auth--websocket) |
| 102 | [Checkpoint Gate B — Backend API/Auth/WebSocket Audit](#phase-102-checkpoint-gate-b--backend-apiauthwebsocket-audit) |
| 5 | [Data Simulator](#phase-5-data-simulator) |
| 6 | [Firmware — ESP32 Project Structure](#phase-6-firmware--esp32-project-structure) |
| 103 | [Checkpoint Gate C — Data Flow Contract Audit (Simulator/Firmware)](#phase-103-checkpoint-gate-c--data-flow-contract-audit-simulatorfirmware) |
| 7 | [Edge — BLE Client & Ingest](#phase-7-edge--ble-client--ingest) |
| 8 | [Edge — Pipeline & Feature Extraction](#phase-8-edge--pipeline--feature-extraction) |
| 9 | [Edge — Classifier & API Client](#phase-9-edge--classifier--api-client) |
| 104 | [Checkpoint Gate D — Edge Pipeline Audit](#phase-104-checkpoint-gate-d--edge-pipeline-audit) |
| 10 | [ML — Data Collection & Labeling](#phase-10-ml--data-collection--labeling) |
| 11 | [ML — Training Script](#phase-11-ml--training-script) |
| 12 | [ML — Model Export & Integration](#phase-12-ml--model-export--integration) |
| 105 | [Checkpoint Gate E — ML/Edge Consistency Audit](#phase-105-checkpoint-gate-e--mledge-consistency-audit) |
| 13 | [Dashboard — Setup & Auth](#phase-13-dashboard--setup--auth) |
| 14 | [Dashboard — Live View](#phase-14-dashboard--live-view) |
| 15 | [Dashboard — Alerts & Shift Summary](#phase-15-dashboard--alerts--shift-summary) |
| 106 | [Checkpoint Gate F — UI + Realtime + Data Integrity Audit](#phase-106-checkpoint-gate-f--ui--realtime--data-integrity-audit) |
| 16 | [Integration & End-to-End Testing](#phase-16-integration--end-to-end-testing) |
| 17 | [Pilot Preparation](#phase-17-pilot-preparation) |
| 18 | [Documentation & Handoff](#phase-18-documentation--handoff) |
| 107 | [Checkpoint Gate G — Final Readiness Audit](#phase-107-checkpoint-gate-g--final-readiness-audit) |

---

## Phase 1: Project Setup & Structure

**Goal:** Create directory structure and base configuration.

### 1.1 Create Directory Structure

**Steps:**
1. Create all folders from project root `D:\Industrial_Wearable_AI`.
2. Ensure no typos; structure must match exactly.

**Folders to create:**
```
firmware/
firmware/src/
edge/
edge/src/
backend/
backend/app/
backend/app/models/
backend/app/schemas/
backend/app/api/
backend/app/services/
backend/alembic/
dashboard/
ml/
ml/data/
ml/data/raw/
ml/data/labeled/
ml/models/
ml/scripts/
```

**Checklist:** [x] All directories exist

---

### 1.2 Create Root .gitignore

**File:** `.gitignore` (project root)

**Requirements:**
- Exclude: `__pycache__/`, `*.pyc`, `venv/`, `.venv/`, `.env`
- Exclude: `node_modules/`, `dist/`, `build/`
- Exclude: `backend/.env`, `edge/.env`
- Exclude: `ml/models/*.joblib`, `ml/data/raw/*.csv`, `*.log`
- Exclude: `.idea/`, `.vscode/`, `.DS_Store`

**Checklist:** [x] .gitignore created and excludes sensitive/generated files

---

### 1.3 Verify Phase 1

- [x] All folders exist
- [x] .gitignore at root

---

### 1.4 Environment Bootstrap (Laptop Prereqs)

**Goal:** Prevent setup surprises later by validating prerequisites now.

**Must have installed on laptop:**
- [x] **Python 3.10+** (check: `python --version`)
- [x] **Node.js 18/20 LTS** (check: `node --version`)
- [x] **Git** (check: `git --version`)
- [x] **PostgreSQL 14/15** *or* **Docker Desktop** (for Postgres in a container)
- [ ] **Bluetooth** support *or* **USB BLE dongle** (not yet validated)

**Steps:**
1. Decide venv strategy:
   - **Option A:** One venv per service (`backend/`, `edge/`, `ml/`) (**recommended**)
   - **Option B:** One shared venv at repo root (simpler, but mixes deps)
2. Decide DB strategy (write it in `docs/DECISIONS.md`):
   - **Option A (recommended):** Docker Postgres
   - **Option B:** Local Postgres install

#### Windows (PowerShell) Notes — Venv Setup

**Create venv per service (recommended):**

```powershell
# Backend
cd d:\Industrial_Wearable_AI\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Edge
cd d:\Industrial_Wearable_AI\edge
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate

# ML
cd d:\Industrial_Wearable_AI\ml
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

**If PowerShell blocks activation** (ExecutionPolicy), run once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Enhancement slot (recommended files):**
- [x] Create `docs/DECISIONS.md` (records decisions and later changes)
- [x] Create `docs/KNOWN_ISSUES.md` (records fixes for common setup issues)

**Checklist:** [x] Prerequisites validated and recorded

---

## Phase 2: Backend — Database & Models

**Goal:** PostgreSQL schema, SQLAlchemy models, Alembic migrations.

**Reference:** `TECHNICAL_STACK_SPEC.md` §3.4 — Database Schema

---

### 2.1 Backend requirements.txt

**File:** `backend/requirements.txt`

**Requirements:**
- fastapi ≥0.100
- uvicorn[standard] ≥0.22
- sqlalchemy[asyncio] ≥2.0
- asyncpg ≥0.28
- alembic ≥1.12
- pydantic ≥2.0
- python-jose[cryptography]
- passlib[bcrypt]
- python-dotenv

**Steps:**
1. Create file with above packages and versions.
2. Run `pip install -r requirements.txt` (use venv recommended).

**Checklist:** [x] requirements.txt created [x] Dependencies install

---

### 2.2 Backend config.py

**File:** `backend/app/config.py`

**Features:**
- Load env from `.env` (python-dotenv).
- Export: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`.
- `CORS_ORIGINS` must be a list (split comma-separated string).
- Default `DATABASE_URL`: `postgresql+asyncpg://postgres:postgres@localhost:5432/wearable_ai`.

**Steps:**
1. Create config module.
2. Read env vars with fallback defaults.
3. Ensure CORS_ORIGINS is list for FastAPI middleware.

**Checklist:** [x] config.py created [x] All vars load correctly

---

### 2.3 Backend database.py

**File:** `backend/app/database.py`

**Features:**
- Create async SQLAlchemy engine from `DATABASE_URL`.
- Create `AsyncSessionLocal` (async session factory).
- Create `Base` for declarative models.
- Implement `get_db()` async generator: yield session, commit on success, rollback on error, close on exit.

**Steps:**
1. Use `create_async_engine`, `async_sessionmaker`, `AsyncSession`.
2. Implement `get_db` as FastAPI dependency.

**Checklist:** [x] database.py created [x] get_db works as dependency

---

### 2.4 Backend Models

**Files:** `backend/app/models/*.py`

**Schema (from TECHNICAL_STACK_SPEC):**

| Table | Key columns |
|-------|-------------|
| workers | id (UUID PK), name, role, device_id (FK nullable), created_at |
| devices | id (UUID PK), hardware_id (unique), worker_id (FK nullable), last_seen_at |
| sessions | id (UUID PK), worker_id (FK), started_at, ended_at, shift_label |
| activity_events | id (UUID PK), session_id (FK), ts, label, risk_ergo, risk_fatigue |
| session_aggregates | session_id (PK,FK), active_pct, idle_pct, adjusting_pct, error_pct, alert_count, updated_at |
| users | id (UUID PK), username (unique), hashed_password, created_at |

**Steps:**
1. Create `models/__init__.py` — export all models.
2. Create `worker.py`, `device.py`, `session.py`, `activity_event.py`, `session_aggregate.py`, `user.py`.
3. Each model: inherit `Base`, set `__tablename__`, define columns per schema.
4. Use `UUID(as_uuid=True)` for UUID columns.
5. Add indexes: `activity_events(session_id, ts)`, `sessions(worker_id, started_at)`.

**Checklist:** [x] All model files created [x] Imports work

---

### 2.5 Alembic Setup

**Steps:**
1. Run `alembic init alembic` from `backend/`.
2. Update `alembic/env.py`: import `Base` and all models; set `target_metadata = Base.metadata`; use `DATABASE_URL` from config.
3. Ensure env.py supports async (use `run_migrations_online` with async engine if needed).
4. Create database: `CREATE DATABASE wearable_ai;` (in PostgreSQL).
5. Run `alembic revision --autogenerate -m "Initial schema"`.
6. Run `alembic upgrade head`.

**Checklist:** [x] Alembic init [x] Migration created [x] Tables exist in PostgreSQL

---

### 2.5A PostgreSQL on Laptop — Supported Setup Options (Pick One)

**Option A: Docker Postgres (Recommended + CHOSEN)**

**Why:** Fast, consistent, avoids local service issues.

**Steps:**
1. Create `backend/docker-compose.yml` with a Postgres 15 service.
2. Start DB: `docker compose up -d` (from `backend/`).
3. Point `DATABASE_URL` to the container (host `localhost`, mapped port).

**Checklist:** [x] Container running [x] Can connect via `DATABASE_URL`

#### Windows (PowerShell) Notes — Docker Compose & Postgres Troubleshooting

**Minimal `backend/docker-compose.yml`:**

```yaml
services:
  postgres:
    image: postgres:15
    container_name: wearable_ai_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: wearable_ai
    ports:
      - "5432:5432"
    volumes:
      - wearable_ai_pgdata:/var/lib/postgresql/data

volumes:
  wearable_ai_pgdata:
```

**Start/stop DB (PowerShell):**

```powershell
cd d:\Industrial_Wearable_AI\backend
docker compose up -d
docker compose ps
docker compose logs -f postgres

# Stop services (keeps data)
docker compose down

# Wipe DB data (ONLY if you want to reset everything)
docker compose down -v
```

**DATABASE_URL for this compose setup:**

```text
postgresql+asyncpg://postgres:postgres@localhost:5432/wearable_ai
```

**If port 5432 is busy:**

- Change compose mapping to `"5433:5432"` and use:\n  `postgresql+asyncpg://postgres:postgres@localhost:5433/wearable_ai`

**If migrations fail because DB isn't ready:**
- Wait ~10 seconds and retry, or watch `docker compose logs -f postgres`.

**Option B: Local PostgreSQL Install**

**Why:** No Docker dependency.

**Steps:**
1. Install PostgreSQL 14/15 locally.
2. Create DB: `wearable_ai`.
3. Set `DATABASE_URL` for local connection.

**Checklist:** [ ] Local DB running [ ] Can connect via `DATABASE_URL`

---

### 2.6 Backend .env.example

**File:** `backend/.env.example`

**Requirements:**
- `DATABASE_URL=postgresql+asyncpg://...`
- `SECRET_KEY=...`
- `CORS_ORIGINS=http://localhost:5173,http://localhost:3000`

**Steps:**
1. Create template.
2. Copy to `.env` and fill real values.

**Checklist:** [x] .env.example created [ ] .env configured (user copies from example)

---

### 2.7 Verify Phase 2

- [x] `alembic upgrade head` succeeds
- [x] Tables: workers, devices, sessions, activity_events, session_aggregates, users exist
- [x] Backend can open a DB session (quick import/run check)

---

## Phase 101: Checkpoint Gate A — Backend DB & Migrations Audit

**Goal:** Confirm Phase 1–2 are complete, correct, and reproducible before writing API logic.

### 101.1 Completion Audit (Must Be True)

- [x] Folder structure exists (Phase 1)
- [x] `.gitignore` excludes `.env`, `ml/data/raw`, `ml/models`, logs
- [x] `backend/requirements.txt` installs cleanly in a fresh venv
- [x] `backend/.env.example` exists and documents required env vars
- [x] Alembic initialized, migrations generated, and `alembic upgrade head` succeeds
- [x] PostgreSQL database `wearable_ai` exists and is reachable from laptop

### 101.2 Dependency Audit

- [x] Python version is 3.10+ (matches stack spec)
- [x] PostgreSQL version is 14/15 (recommended)
- [x] No missing packages when running `uvicorn` import checks

### 101.3 Schema Audit (No Missing Tables/Indexes)

**Check that these tables exist:** `workers`, `devices`, `sessions`, `activity_events`, `session_aggregates`, `users`.

**Check indexes:**
- [x] `activity_events(session_id, ts)`
- [x] `sessions(worker_id, started_at)`

### 101.4 Enhancement Slot (Optional but Recommended)

If you notice issues, improve now (do not proceed until fixed):

- **Enhancement ideas**:
  - [x] Add enum constraint for activity labels (ActivityLabel enum in model)
  - [x] Add timestamps (`created_at`) where needed (workers, users, session_aggregates)
  - [ ] Add DB constraints (non-null where appropriate) — deferred
  - [ ] Add a lightweight `Makefile`/scripts for `db-migrate`, `db-up`, `db-down` (optional)

### 101.5 Gate Pass Criteria

- [x] A fresh clone + venv + postgres + alembic results in the schema with no manual edits

---

## Phase 3: Backend — API Endpoints

**Goal:** FastAPI app, POST /events, GET workers/sessions/summary.

**Reference:** `TECHNICAL_STACK_SPEC.md` §4 — Data Formats & Protocols

---

### 3.1 Pydantic Schemas

**Files:** `backend/app/schemas/*.py`

**Requirements:**

| Schema | Purpose |
|--------|---------|
| ActivityEventIn | ts (int), label (str), risk_ergo (bool), risk_fatigue (bool) |
| EventBatch | device_id (optional), worker_id (str), events (list of ActivityEventIn) |
| WorkerOut | id, name, role, device_id, created_at |
| SessionOut | id, worker_id, started_at, ended_at, shift_label |
| SessionSummaryOut | session_id, worker_id, active_pct, idle_pct, adjusting_pct, error_pct, alert_count |

**Steps:**
1. Create `schemas/__init__.py`.
2. Create `events.py`, `workers.py`, `sessions.py` with Pydantic models.
3. Use `from_attributes = True` for ORM response models.

**Checklist:** [x] All schemas created

---

### 3.2 Event Service (Aggregation)

**File:** `backend/app/services/event_service.py`

**Features:**
- Function `update_session_aggregate(db, session_id)`.
- Query `activity_events` for session; group by label; count each.
- Compute: active_pct (sewing+adjusting), idle_pct, adjusting_pct, error_pct.
- Count events where risk_ergo or risk_fatigue = true → alert_count.
- Upsert `session_aggregates` row for session.

**Steps:**
1. Use SQLAlchemy select, group_by, func.count.
2. Create or update SessionAggregate.
3. Call from events API after inserting events.

**Checklist:** [x] event_service.py created [x] Aggregation logic correct

---

### 3.3 API Routes

**File:** `backend/app/api/events.py`

**Features:**
- `POST /api/events` — accept EventBatch.
- Resolve or create Worker by worker_id (e.g. use name as worker_id for MVP).
- Resolve or create active Session (no ended_at) for worker.
- Insert each event into activity_events.
- Call `update_session_aggregate`.
- Return `{status: "ok", count: N}`.

**Steps:**
1. Implement route with Depends(get_db).
2. Handle worker/session lookup or creation.
3. Bulk insert events; update aggregates.

**Checklist:** [x] POST /api/events works

---

**File:** `backend/app/api/workers.py`

**Features:**
- `GET /api/workers` — return list of workers (WorkerOut).

**Steps:**
1. Query Worker; return as list.

**Checklist:** [x] GET /api/workers works

---

**File:** `backend/app/api/sessions.py`

**Features:**
- `GET /api/sessions` — return list of sessions (SessionOut), ordered by started_at desc, limit 50.
- `GET /api/sessions/{session_id}/summary` — return SessionSummaryOut; 404 if not found.

**Steps:**
1. Implement both routes.
2. For summary: join or query SessionAggregate + Session.

**Checklist:** [x] Both session routes work

---

### 3.4 Main FastAPI App

**File:** `backend/app/main.py`

**Features:**
- Create FastAPI app.
- Add CORS middleware (allow CORS_ORIGINS).
- Include routers: events, workers, sessions.
- `GET /` — health check returning `{status: "ok"}`.

**Steps:**
1. Create app; add middleware; include routers.
2. Run with `uvicorn app.main:app --reload`.

**Checklist:** [x] Server starts [x] POST /events, GET /workers work (test with curl/Postman)

---

### 3.4A Developer Ergonomics (Recommended Enhancements)

**Goal:** Make integration and debugging faster (strongly recommended).

- [x] Confirm FastAPI OpenAPI is accessible at `/docs` and shows correct schemas
- [x] Add basic structured logging (request path, status, errors)
- [x] Add `/api/version` endpoint returning `{service, version, build_time}` (optional but helpful)

**Checklist:** [x] `/docs` loads [x] logs are readable during debugging

---

### 3.5 Verify Phase 3

- [x] POST /api/events stores events and updates aggregates
- [x] GET /api/sessions/{id}/summary returns correct percentages

---

## Phase 4: Backend — Auth & WebSocket

**Goal:** JWT login, WebSocket /ws/live for live state broadcast.

---

### 4.1 Auth Schema & Route

**File:** `backend/app/schemas/auth.py`

**Requirements:**
- LoginRequest: username, password.
- TokenResponse: access_token, token_type.

**File:** `backend/app/api/auth.py`

**Features:**
- `POST /api/auth/login` — accept username, password.
- Lookup User; verify password with bcrypt.
- Generate JWT (sub=user_id, exp=now+expire_minutes).
- Return TokenResponse.

**Steps:**
1. Use passlib.CryptContext for verify.
2. Use python-jose jwt.encode with SECRET_KEY, ALGORITHM.

**Checklist:** [x] Login returns JWT

---

### 4.2 Seed Default User

**File:** `backend/seed_user.py`

**Features:**
- Create User with username="admin", hashed_password=bcrypt("admin123") if not exists.
- Run as script: `python seed_user.py`.

**Steps:**
1. Use async session; check if admin exists; insert if not.
2. Run after migrations.

**Checklist:** [x] Admin user exists [x] Login with admin/admin123 works

---

### 4.3 WebSocket Hub

**File:** `backend/app/services/websocket_hub.py`

**Features:**
- Class or module with: list of active WebSocket connections.
- `connect(websocket)` — accept and add to list.
- `disconnect(websocket)` — remove from list.
- `broadcast(message: dict)` — send JSON to all connections.

**Steps:**
1. Implement connection manager.
2. Use `await websocket.send_json(message)` for broadcast.

**Checklist:** [x] Hub created

---

### 4.4 WebSocket Endpoint & Broadcast on Events

**Steps:**
1. In `main.py`: add `@app.websocket("/ws/live")` — accept connection, call hub.connect, keep alive (receive loop), on disconnect call hub.disconnect.
2. In `api/events.py`: after inserting events, call `hub.broadcast({worker_id, name, current_state, risk_ergo, risk_fatigue, updated_at})` with latest event data.

**Checklist:** [x] WebSocket accepts connections [x] Clients receive broadcast when events posted

---

### 4.5 Verify Phase 4

- [x] Login returns JWT
- [x] WebSocket client receives messages when POST /events

---

## Phase 102: Checkpoint Gate B — Backend API/Auth/WebSocket Audit

**Goal:** Confirm Phase 1–4 deliver a working backend contract before building Edge/Dashboard.

### 102.1 Completion Audit (Must Be True)

- [x] Backend starts: `uvicorn app.main:app --reload`
- [x] `GET /` health returns `{status: "ok"}` (or equivalent)
- [x] `POST /api/events` accepts the defined payload format
- [x] `GET /api/workers` returns workers (even if created implicitly by events)
- [x] `GET /api/sessions` returns sessions
- [x] `GET /api/sessions/{id}/summary` returns aggregates or 404 correctly
- [x] `POST /api/auth/login` returns JWT for seeded admin
- [x] `/ws/live` accepts connections and broadcasts on new events

### 102.2 Contract Audit (Match the Spec)

**Confirm these match `TECHNICAL_STACK_SPEC.md` §4.2 and §4.3:**
- [x] `/api/events` request shape (batch)
- [x] WebSocket message shape (live state)
- [x] Label set includes: `sewing`, `idle`, `adjusting`, `error`, `break`

### 102.3 Minimal Test Checklist (Manual)

- [x] Post 10 events for W01; verify DB rows count increased
- [x] Open WebSocket client; post event; verify live message received
- [x] Verify aggregate percentages update after additional events

### 102.4 Enhancement Slot (Optional but Recommended)

- **Enhancement ideas**:
  - [ ] Add input validation for labels (reject unknown label)
  - [ ] Add request size limits / batching limits
  - [ ] Add basic logging (request count, errors)
  - [ ] Add simple API key auth for edge (optional for MVP)

### 102.5 Gate Pass Criteria

- [x] Backend contract is stable enough for Edge/Dashboard integration (no breaking endpoint changes expected)

---

## Phase 5: Data Simulator

**Goal:** Script that POSTs mock activity events to backend for testing without hardware.

---

### 5.1 Simulator Script

**File:** `ml/simulator.py`

**Features:**
- Configurable: BASE_URL (default localhost:8000), worker_id (default "W01"), duration_sec, interval_sec.
- Generate events with random label from [sewing, idle, adjusting, error, break].
- Each event: ts (Unix ms), label, risk_ergo (false), risk_fatigue (optional, e.g. when idle).
- POST batch to `POST /api/events` in request body format: `{worker_id, events: [{ts, label, risk_ergo, risk_fatigue}]}`.

**Steps:**
1. Use requests or aiohttp.
2. Loop for duration; every interval, create event(s) and POST.
3. Allow command-line args or env for config.

**Checklist:** [x] simulator.py runs [x] Events appear in DB and trigger WebSocket broadcast

---

### 5.2 ML requirements.txt

**File:** `ml/requirements.txt`

**Requirements:** requests, pandas, numpy, scikit-learn, joblib (for later phases).

**Checklist:** [x] ml/requirements.txt created

---

### 5.3 Verify Phase 5

- [x] Run simulator; backend receives events; WebSocket clients get updates

---

## Phase 6: Firmware — ESP32 Project Structure

**Goal:** PlatformIO/Arduino project structure. **Replace main.cpp with your implementation when hardware is ready.**

**Reference:** `TECHNICAL_STACK_SPEC.md` §3.1, §4.1

---

### 6.1 PlatformIO Config

**File:** `firmware/platformio.ini`

**Requirements:**
- Platform: espressif32, board: esp32dev, framework: arduino.
- Libraries: Adafruit MPU6050, Adafruit Unified Sensor, ArduinoJson, NimBLE or BluetoothSerial (for BLE).

**Steps:**
1. Create platformio.ini with correct env and lib_deps.
2. Ensure BLE library is included.

**Checklist:** [x] platformio.ini created [ ] `pio run` compiles (requires PlatformIO: `pip install platformio`)

---

### 6.2 Placeholder main.cpp

**File:** `firmware/src/main.cpp`

**Requirements (for final implementation):**
1. Read MPU6050 (ax, ay, az, gx, gy, gz) at ~25 Hz.
2. Read DHT11/DS18B20 (temp) at ~0.2 Hz.
3. Pack JSON: `{worker_id, ts, ax, ay, az, gx, gy, gz, temp}`.
4. Send via BLE (GATT notify or write).

**Steps for now:**
1. Create placeholder: setup prints message; loop delays. Compiles but does nothing.
2. **Replace entirely** when you have ESP32 + MPU6050 + temp sensor wired.

**Checklist:** [x] Placeholder compiles [ ] Replace with real implementation later

---

### 6.3 Firmware README

**File:** `firmware/README.md`

**Requirements:** Document hardware, build/upload commands, expected JSON payload format (from TECHNICAL_STACK_SPEC §4.1).

**Checklist:** [x] README created

---

### 6.4 Verify Phase 6

- [ ] `pio run` succeeds (run after PlatformIO install; first run downloads ESP32 toolchain)

---

## Phase 103: Checkpoint Gate C — Data Flow Contract Audit (Simulator/Firmware)

**Goal:** Lock the data contracts early to prevent data loss and rework later.

### 103.1 Completion Audit (Must Be True)

- [x] Simulator can post valid `/api/events` payload repeatedly without errors
- [x] If firmware placeholder exists: it compiles (even if it does not stream yet)

### 103.2 Data Contract Audit

Confirm **two distinct payload layers** are defined and understood:

1. **Wearable → Edge (raw samples)** (`TECHNICAL_STACK_SPEC.md` §4.1)
   - [x] `worker_id`, `ts`, `ax,ay,az`, `gx,gy,gz`, `temp`
2. **Edge → Backend (events)** (`TECHNICAL_STACK_SPEC.md` §4.2)
   - [x] `worker_id`, optional `device_id`, `events[{ts,label,risk_ergo,risk_fatigue}]`

### 103.3 Anti-Data-Loss Rules (Must Adopt)

- [ ] **Timestamps** are in Unix milliseconds everywhere
- [ ] **worker_id** is consistent across layers (same string/ID)
- [ ] Decide now: do we store raw IMU in DB? (MVP: **No**, store labels only; raw CSV only for training/debug.)
- [ ] Simulator and Edge must never silently change label names

### 103.4 Enhancement Slot

- **Enhancement ideas**:
  - [ ] Add a small `docs/DATA_CONTRACTS.md` summarizing raw vs events payload (optional)
  - [ ] Add sample payloads in docs for quick copy/paste tests (optional)

### 103.5 Gate Pass Criteria

- [ ] Everyone can answer: “What is raw sample payload?” and “What is backend event payload?” without ambiguity

---

## Phase 7: Edge — BLE Client & Ingest

**Goal:** Receive BLE stream (or simulated input) and buffer samples.

---

### 7.1 Edge requirements.txt

**File:** `edge/requirements.txt`

**Requirements:** numpy, pandas, scikit-learn, joblib, bleak, aiohttp, python-dotenv.

**Checklist:** [x] edge/requirements.txt created

---

### 7.2 Edge .env.example

**File:** `edge/.env.example`

**Requirements:** BACKEND_URL, MODEL_PATH, BLE_DEVICE_ID, WINDOW_SECONDS, OVERLAP, WORKER_ID.

**Checklist:** [x] .env.example created

---

### 7.3 BLE Client

**File:** `edge/src/ble_client.py`

**Features:**
- `read_ble_stream(device_id, callback, use_simulator)` — async.
- If use_simulator or no device_id: generate fake samples in loop (worker_id, ts, ax, ay, az, gx, gy, gz, temp) at ~25 Hz; call callback for each.
- If real BLE: connect to device_id, read GATT characteristic, parse JSON, call callback.
- Sample format must match TECHNICAL_STACK_SPEC §4.1.

**Steps:**
1. Use bleak for BLE (BleakClient, start_notify).
2. Simulator mode: random or patterned values; asyncio.sleep(0.04) for ~25 Hz.
3. Real mode: implement when firmware is ready; GATT UUID from firmware.

**Checklist:** [x] ble_client has simulator fallback [x] Real BLE ready for when firmware available

---

### 7.4 Sample Buffer

**File:** `edge/src/buffer.py`

**Features:**
- Class SampleBuffer: max_seconds, sample_rate.
- `append(sample)` — add to ring buffer (maxlen = max_seconds * sample_rate).
- `get_window(num_samples)` — return last num_samples as list, or None if insufficient.

**Steps:**
1. Use collections.deque with maxlen.
2. Ensure thread-safe or single-threaded async usage.

**Checklist:** [x] Buffer holds samples correctly

---

### 7.5 Verify Phase 7

- [x] Simulator mode produces samples
- [x] Buffer fills and returns windows

---

## Phase 8: Edge — Pipeline & Feature Extraction

**Goal:** Filter, sliding window, feature extraction. **Must match ML training pipeline exactly.**

**Reference:** `TECHNICAL_STACK_SPEC.md` §3.5 — ML Pipeline

---

### 8.1 Feature Extractor

**File:** `edge/src/feature_extractor.py`

**Features:**
- `extract_features(samples: list) -> np.ndarray` — input list of sample dicts with ax,ay,az,gx,gy,gz.
- Per axis: mean, std, min, max, zero_crossing_rate.
- Output: 1D array of 30 floats (6 axes × 5 features).
- Zero-crossing rate: count sign changes / (2*(n-1)).

**Steps:**
1. Convert to numpy arrays per axis.
2. Compute features; concatenate.
3. **Critical:** Same logic as ml/scripts/feature_extraction.py.

**Checklist:** [x] Feature vector length matches training

---

### 8.2 Pipeline

**File:** `edge/src/pipeline.py`

**Features:**
- Low-pass filter (e.g. alpha=0.3 exponential moving average) on each axis.
- `process_window(samples)` — apply filter, call extract_features, return feature vector.

**Steps:**
1. Implement simple low-pass.
2. Apply to each axis before feature extraction.

**Checklist:** [x] process_window returns correct shape

---

### 8.3 Verify Phase 8

- [x] extract_features returns 30-dim vector
- [x] Pipeline runs without error

---

## Phase 9: Edge — Classifier & API Client

**Goal:** Load model (or rule-based fallback), predict label, POST to backend.

---

### 9.1 Classifier

**File:** `edge/src/classifier.py`

**Features:**
- `load_model(path)` — load joblib model if path exists; else return None.
- `predict(model, features) -> str` — if model: model.predict; map index to label (sewing, idle, adjusting, error, break). If no model: rule-based (e.g. low variance→idle, high→sewing).
- Labels must match backend enum.

**Steps:**
1. Use joblib.load.
2. Handle model.classes_ for label mapping.
3. Rule-based: use variance or simple thresholds.

**Checklist:** [x] Predict returns valid label

---

### 9.2 API Client

**File:** `edge/src/api_client.py`

**Features:**
- `post_events(worker_id, events) -> bool` — POST to BACKEND_URL/api/events.
- Payload: `{worker_id, events: [{ts, label, risk_ergo, risk_fatigue}]}`.
- Return True if status 200.

**Steps:**
1. Use aiohttp or requests.
2. Read BACKEND_URL from env.

**Checklist:** [ ] POST succeeds when backend running

---

### 9.3 Edge Main

**File:** `edge/src/main.py`

**Features:**
- Load model from MODEL_PATH.
- Create SampleBuffer (WINDOW_SECONDS, SAMPLE_RATE=25).
- On each sample from BLE client: append to buffer; when buffer has enough (WINDOW_SAMPLES), extract window with OVERLAP step; process_window → features; predict → label; optionally apply ergo/fatigue rules; batch events; when batch size ≥ N, post_events.
- Run read_ble_stream in simulator mode if no BLE_DEVICE_ID.

**Steps:**
1. Wire: ble_client callback → buffer → pipeline → classifier → api_client.
2. Use asyncio.
3. Config from env.

**Checklist:** [x] Edge runs; posts events to backend; [ ] dashboard updates (Phase 14)

---

### 9.4 Verify Phase 9

- [x] Edge in simulator mode posts to backend
- [ ] Dashboard shows live updates (Phase 14)

---

## Phase 104: Checkpoint Gate D — Edge Pipeline Audit

**Goal:** Confirm Edge is stable and correct before starting ML training and UI work at scale.

### 104.1 Completion Audit (Must Be True)

- [ ] Edge runs in simulator mode end-to-end (samples → features → label → POST /api/events)
- [ ] Backend receives events continuously without errors
- [ ] WebSocket broadcasts (from backend) continue working while edge runs

### 104.2 Performance & Stability Checks

- [ ] Edge does not leak memory over 10–15 minutes
- [ ] Event batching works (does not spam backend at 25 Hz)
- [ ] If backend is down, edge logs errors and continues/retries (no crash)

### 104.3 Consistency Checks

- [ ] Feature vector shape is stable (always 30 floats)
- [ ] Labels always from allowed set (no typos)
- [ ] `ts` strictly increasing over time (per worker)

### 104.4 Enhancement Slot

- **Enhancement ideas**:
  - [ ] Add local CSV logging option on edge (for debugging)
  - [ ] Add reconnect logic for BLE (when firmware is ready)
  - [ ] Add config validation on startup (env var sanity checks)

### 104.5 Gate Pass Criteria

- [ ] Edge can run unattended for 30 minutes with no crashes and stable event flow

---

## Phase 10: ML — Data Collection & Labeling

**Goal:** Collect raw CSV; label segments for training.

---

### 10.1 Raw Data Collector

**File:** `ml/scripts/collect_raw.py`

**Features:**
- Write CSV to ml/data/raw/ with columns: timestamp, ax, ay, az, gx, gy, gz, temp.
- Data source: pipe from BLE/simulator or generate dummy for testing.
- Filename: raw_YYYYMMDD_HHMMSS.csv.

**Steps:**
1. Implement CSV writer.
2. In real use: connect to edge or BLE and log samples.

**Checklist:** [x] Raw CSV produced

---

### 10.1A Raw CSV Validation (Recommended)

**File:** `ml/scripts/validate_raw_csv.py`

**Goal:** Catch data issues early (prevents training failures and “silent bad data”).

**Features:**
- Validate required columns: `timestamp, ax, ay, az, gx, gy, gz, temp`
- Validate `timestamp` is numeric and mostly monotonic increasing
- Validate no extreme missing values / NaNs (report counts)
- Print a short summary: row count, time span, sample rate estimate

**Steps:**
1. Load a raw CSV file from `ml/data/raw/`.
2. Run validations and exit non-zero on critical failure.

**Checklist:** [x] Validation script exists [ ] Used on every new raw dataset

---

### 10.2 Labeling Guide

**File:** `ml/data/labeled/README.md`

**Features:**
- Document format: start_ts, end_ts, label (sewing, idle, adjusting, error, break).
- Process: record video, sync timestamps, assign labels per segment.

**Checklist:** [x] README created

---

### 10.3 Verify Phase 10

- [x] Raw data format documented
- [x] Labeling process clear

---

## Phase 11: ML — Training Script

**Goal:** Load labeled data, extract features, train classifier, export joblib.

**Reference:** `TECHNICAL_STACK_SPEC.md` §3.5

---

### 11.1 Feature Extraction (ML)

**File:** `ml/scripts/feature_extraction.py`

**Features:**
- `extract_features_from_window(df)` — same logic as edge feature_extractor.
- Input: DataFrame with ax,ay,az,gx,gy,gz columns.
- Output: 1D numpy array (30 features).

**Steps:**
1. Copy logic from edge; ensure identical output.

**Checklist:** [x] Matches edge feature extractor

---

### 11.2 Training Script

**File:** `ml/scripts/train.py`

**Features:**
- Load raw CSV and labels CSV.
- For each labeled segment: extract window from raw, compute features, assign label.
- Train/val split (e.g. 80/20).
- Train RandomForestClassifier (or XGBoost).
- Evaluate: accuracy, classification_report.
- Export model to ml/models/activity_model.joblib.
- Target accuracy ≥85%.

**Steps:**
1. Merge raw + labels by timestamp range.
2. Build X, y arrays.
3. train_test_split; fit; evaluate; joblib.dump.

**Checklist:** [x] train.py runs [x] Model exported [x] Accuracy acceptable

---

### 11.2A Model Card (Recommended)

**File:** `ml/models/MODEL_CARD.md`

**Goal:** Prevent “which model is this?” confusion during demo/pilot and future retraining.

**Must include:**
- Training date/time
- Dataset(s) used (raw CSV filenames + label filenames)
- Window size + overlap
- Feature list + order (must match edge)
- Model type + key hyperparameters
- Metrics: accuracy, per-class precision/recall/F1
- Known limitations / next improvements

**Checklist:** [x] MODEL_CARD.md created for each exported model

---

### 11.3 Verify Phase 11

- [x] activity_model.joblib created
- [x] Model loads in edge and produces predictions

---

## Phase 12: ML — Model Export & Integration

**Goal:** Edge loads model; end-to-end with ML predictions.

---

### 12.1 Integration Steps

1. Set MODEL_PATH in edge/.env to path to activity_model.joblib.
2. Ensure classifier maps model output (index or string) to label string correctly.
3. Run edge; verify predictions use model (not only rules).

**Checklist:** [x] Edge uses ML model when available [x] Predictions reasonable

---

## Phase 105: Checkpoint Gate E — ML/Edge Consistency Audit

**Goal:** Ensure training pipeline and edge inference pipeline are aligned (no silent mismatch).

### 105.1 Completion Audit (Must Be True)

- [x] Raw CSV format matches expected columns: timestamp, ax, ay, az, gx, gy, gz, temp
- [x] Labels file format exists and is usable (start_ts,end_ts,label)
- [x] A model is exported (`.joblib`) and loadable
- [x] Edge loads the model successfully

### 105.2 Feature Parity Audit (Critical)

- [x] Feature extractor in ML and Edge compute the **same features in the same order**
- [x] Windowing parameters are documented (window seconds, overlap)
- [x] Any filtering (low-pass) is either applied consistently in both or documented clearly

### 105.3 Evaluation Gate

- [x] Report accuracy and per-class F1 on a hold-out set
- [x] Target: ≥85% accuracy for MVP (or document why lower and what’s next)

### 105.4 Enhancement Slot

- **Enhancement ideas**:
  - [ ] Add confusion matrix export for analysis
  - [ ] Add “unknown” class if misclassifications are frequent
  - [ ] Add per-worker calibration notes (future)

### 105.5 Gate Pass Criteria

- [x] Edge inference results are consistent with offline evaluation expectations

---

## Phase 13: Dashboard — Setup & Auth

**Goal:** React app, Vite, login page, auth flow.

**Reference:** `TECHNICAL_STACK_SPEC.md` §3.6

---

### 13.1 Create React App

**Steps:**
1. `npm create vite@latest dashboard -- --template react-ts`
2. `cd dashboard && npm install`
3. Install: react-router-dom, axios, recharts, zustand, react-hot-toast

**Checklist:** [x] Dashboard project created

---

### 13.2 API Client

**File:** `dashboard/src/api/client.ts`

**Features:**
- Axios instance with baseURL from VITE_API_URL.
- Request interceptor: add Authorization header with Bearer token from localStorage.

**Checklist:** [x] API client configured

---

### 13.3 Auth API

**File:** `dashboard/src/api/auth.ts`

**Features:**
- `login(username, password)` — POST /api/auth/login; return access_token.

**Checklist:** [x] login function works

---

### 13.4 Login Page

**File:** `dashboard/src/pages/Login.tsx`

**Features:**
- Form: username, password.
- On submit: call login; store token in localStorage; redirect to /.
- On error: show message.

**Checklist:** [x] Login page renders [x] Login flow works

---

### 13.5 App Routing

**File:** `dashboard/src/App.tsx`

**Features:**
- React Router: /login, / (protected).
- ProtectedRoute: redirect to /login if no token.
- Routes: Login, LiveView (or home).

**Checklist:** [x] Routing works [x] Protected route redirects when not logged in

---

### 13.6 Dashboard .env

**File:** `dashboard/.env`

**Requirements:** VITE_API_URL, VITE_WS_URL (for WebSocket).

**Checklist:** [x] .env configured

---

### 13.7 Verify Phase 13

- [x] npm run dev starts dashboard
- [x] Login with admin/admin123; redirect to /

---

## Phase 14: Dashboard — Live View

**Goal:** WebSocket connection, worker cards, live state display.

---

### 14.1 WebSocket Hook

**File:** `dashboard/src/hooks/useWebSocket.ts`

**Features:**
- Connect to VITE_WS_URL on mount.
- On message: parse JSON; update state (worker_id → {worker_id, name, current_state, risk_ergo, risk_fatigue, updated_at}).
- Return map or list of worker states.
- Cleanup: close WebSocket on unmount.

**Checklist:** [x] Hook connects and receives messages

---

### 14.2 Live View Page

**File:** `dashboard/src/pages/LiveView.tsx`

**Features:**
- Use useWebSocket.
- Display worker cards: name, current_state, risk badges (Ergo, Fatigue).
- Show "Waiting for data" when no workers.
- Layout: grid or flex of cards.

**Checklist:** [x] Live view shows workers [x] Updates when simulator/edge runs

---

### 14.3 Verify Phase 14

- [x] Run simulator; worker cards appear and update

---

## Phase 15: Dashboard — Alerts & Shift Summary

**Goal:** Alerts panel, shift summary, sessions page.

---

### 15.1 Alerts Panel

**File:** `dashboard/src/components/AlertsPanel.tsx`

**Features:**
- Use worker state from WebSocket or context.
- Filter workers where risk_ergo or risk_fatigue is true.
- Display list: worker name, risk type(s).

**Checklist:** [x] Alerts panel shows active alerts

---

### 15.2 Sessions API

**File:** `dashboard/src/api/sessions.ts`

**Features:**
- `getSessions()` — GET /api/sessions.
- `getSessionSummary(sessionId)` — GET /api/sessions/{id}/summary.

**Checklist:** [x] API functions work

---

### 15.3 Sessions / Shift Summary Page

**File:** `dashboard/src/pages/Sessions.tsx` (or similar)

**Features:**
- Fetch sessions list.
- Allow selecting session.
- Fetch and display summary: active_pct, idle_pct, etc. per worker/session.
- Table or chart.

**Steps:**
1. Add route /sessions.
2. Implement page with session selector and summary display.

**Checklist:** [x] Sessions page works [x] Summary displays correctly

---

### 15.4 Verify Phase 15

- [x] Alerts show when risk flags true
- [x] Shift summary displays

---

## Phase 106: Checkpoint Gate F — UI + Realtime + Data Integrity Audit

**Goal:** Confirm the supervisor experience works and UI does not hide backend/edge issues.

### 106.1 Completion Audit (Must Be True)

- [x] Login works reliably
- [x] Live view updates in real time via WebSocket
- [x] Alerts panel reflects risk flags accurately
- [x] Sessions list loads and summaries display

### 106.2 UX Integrity Checks

- [x] "Waiting for data" state is clear (no blank UI confusion)
- [x] WebSocket disconnect/reconnect is handled (shows status or retries)
- [x] Errors are visible (toast/banner) rather than silent failures

### 106.3 Data Integrity Checks (UI ↔ Backend)

- [x] Worker displayed state matches last posted event label
- [x] Session summary values match database aggregates
- [x] Time displayed/used matches Unix ms logic (no timezone confusion)

### 106.4 Enhancement Slot

- **Enhancement ideas**:
  - [x] Add connection status indicator (WS connected/disconnected)
  - [x] Add "last updated" time per worker card
  - [x] Add basic filters (by state, by risk)

### 106.5 Gate Pass Criteria

- [x] Supervisor can answer: "Who is idle?" and "Who is at risk?" within 30 seconds using the UI

---

## Phase 16: Integration & End-to-End Testing

**Goal:** Full stack runs; no errors; latency acceptable.

---

### 16.1 Run Order

1. Start PostgreSQL.
2. Backend: `cd backend && uvicorn app.main:app --reload`
3. Edge: `cd edge && python -m src.main` (or equivalent)
4. Dashboard: `cd dashboard && npm run dev`
5. Simulator (optional): `python ml/simulator.py` — or edge in simulator mode.
6. Open dashboard in browser.

---

### 16.2 Verification Checklist

- [x] Backend: POST /events, GET /workers, GET /sessions, WebSocket work
- [x] Edge: Posts events; dashboard updates
- [x] Dashboard: Login, live view, alerts, shift summary
- [x] End-to-end latency: motion/simulator → dashboard < 5 s
- [x] No console errors; no crashes

---

### 16.3 Regression Checklist (Run After Any Mid-Phase Enhancement)

Whenever you add something “in between phases”, re-run this minimum set:

- [x] Backend still starts; `/docs` loads; core endpoints still visible
- [x] Simulator still posts to `/api/events`
- [x] WebSocket still broadcasts on new events
- [x] Dashboard live view still updates from WebSocket
- [x] Session summary still returns valid percentages

**Gate pass criteria:** [x] All above checks pass before proceeding to next phase

---

## Phase 17: Pilot Preparation

**Goal:** Ready for real deployment.

---

### 17.1 Checklist

- [ ] Replace firmware/src/main.cpp with final ESP32 implementation when hardware ready
- [x] Create .env for backend, edge with production values (see PILOT_PREP.md)
- [x] Seed admin user; change default password (change_password.py)
- [x] Test with multiple worker_ids (2–5)
- [x] Document run order for pilot (RUN_ORDER.md)

---

### 17.2 Run Order Document

**File:** `docs/RUN_ORDER.md`

**Requirements:** Step-by-step instructions to start all services for pilot.

**Checklist:** [x] RUN_ORDER.md created

---

## Phase 18: Documentation & Handoff

**Goal:** Project complete; docs updated.

---

### 18.1 Final Checklist

- [x] README.md at project root with setup instructions
- [x] All .env.example files present and documented
- [x] MASTER_PLAN phases completed
- [ ] firmware main.cpp replaced when hardware ready

---

### 18.2 Project README

**File:** `README.md` (project root)

**Requirements:**
- Project description
- Stack summary (ESP32, Python edge, FastAPI, React)
- Quick start: reference MASTER_PLAN, RUN_ORDER
- Note: replace firmware main.cpp when hardware ready

**Checklist:** [x] README complete

---

## Phase 107: Checkpoint Gate G — Final Readiness Audit

**Goal:** Ensure nothing is missing before pilot/demo, including enhancements discovered mid-way.

### 107.1 Full Completion Audit

- [x] All `.env.example` files exist and match actual `.env` keys used
- [x] Backend migrations are up to date and reproducible
- [x] Backend endpoints stable and documented
- [x] Edge runs in simulator mode and (if ready) BLE mode
- [x] ML training pipeline reproducible (document dataset paths and steps)
- [x] Dashboard stable, real-time working

### 107.2 Security / Safety Basics (MVP)

- [ ] Default admin password changed (run `change_password.py admin` before pilot)
- [x] `.env` not committed to git
- [x] CORS restricted to expected origins (not wildcard unless necessary for dev)

### 107.3 Pilot Checklist (Operational)

- [x] Run order documented (`docs/RUN_ORDER.md`)
- [x] Backup plan: what if BLE fails? (fall back to simulator or wired logging)
- [x] Logging locations known (where to find backend/edge logs)

### 107.4 Enhancement Close-Out

- [x] Any enhancement discovered during Gates A–F is either implemented **or** explicitly deferred in a note

### 107.5 Gate Pass Criteria

- [x] You can demo end-to-end flow on the laptop from a cold start in ≤15 minutes


## Summary: Files by Phase

| Phase | Files to Create/Implement |
|-------|---------------------------|
| 1 | .gitignore, directories, docs/DECISIONS.md (recommended), docs/KNOWN_ISSUES.md (recommended) |
| 2 | backend: requirements, config, database, models (6), alembic, .env.example, backend/docker-compose.yml (if Docker DB) |
| 3 | backend: schemas (events, workers, sessions), event_service, api (events, workers, sessions), main |
| 4 | backend: schemas/auth, api/auth, seed_user, websocket_hub, main updates |
| 5 | ml/simulator.py, ml/requirements.txt |
| 6 | firmware: platformio.ini, src/main.cpp, README |
| 7 | edge: requirements, .env.example, ble_client, buffer, edge/README.md (recommended) |
| 8 | edge: feature_extractor, pipeline |
| 9 | edge: classifier, api_client, main |
| 10 | ml: collect_raw, labeled/README, validate_raw_csv.py (recommended) |
| 11 | ml: feature_extraction, train |
| 12 | (integration), ml/models/MODEL_CARD.md (recommended) |
| 13 | dashboard: api/client, api/auth, Login, App, .env |
| 14 | dashboard: useWebSocket, LiveView |
| 15 | dashboard: AlertsPanel, api/sessions, Sessions page |
| 16 | (testing) |
| 17 | docs/RUN_ORDER.md |
| 18 | README.md |

---

## Reference Documents

- **TECHNICAL_STACK_SPEC.md** — Data formats (§4), API contracts, schema (§3.4), ML pipeline (§3.5)
- **IMPLEMENTATION_PLAN.md** — High-level phases and timeline
- **TECHNICAL_STACK_CLARIFIED.md** — Stack choices and rationale

---

**End of Master Plan. Implement each file per the Features and Steps. Code at implementation time to match current requirements.**
