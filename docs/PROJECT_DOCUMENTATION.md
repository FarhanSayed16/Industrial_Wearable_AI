# Industrial Wearable AI — Complete Project Documentation

**Purpose:** Single reference for everything built in the project: idea, architecture, components, features, setup, APIs, and troubleshooting.  
**Last updated:** 2026-02

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [What Was Built (by Component)](#3-what-was-built-by-component)
4. [Features Delivered](#4-features-delivered)
5. [Hardware & Firmware](#5-hardware--firmware)
6. [How to Run the Project](#6-how-to-run-the-project)
7. [APIs Reference](#7-apis-reference)
8. [Data Flow](#8-data-flow)
9. [Configuration](#9-configuration)
10. [Troubleshooting](#10-troubleshooting)
11. [Related Documents](#11-related-documents)

---

## 1. Project Overview

### 1.1 Goal

**Industrial Wearable AI** is an AI-driven wearable system for **textile manufacturing**: real-time activity recognition, risk monitoring (ergonomics, fatigue), and a supervisor dashboard. It targets low-cost, human-centric monitoring for SMEs where full Industry 4.0 solutions are out of reach.

### 1.2 Problem Addressed

- No real-time data on worker activity and shop-floor conditions.
- Safety issues from repetitive tasks and poor ergonomics.
- Limited visibility into who is working, idle, or at risk.

### 1.3 Solution at a Glance

| Layer | Role |
|-------|------|
| **Wearable** | ESP32 + IMU (MPU6050/MPU9250) + optional temp sensor; streams raw accel/gyro over BLE. |
| **Edge** | Python on laptop: BLE client, sliding-window feature extraction, ML (or rule-based) classifier → activity label + risk flags; posts events and sensor snapshots to backend. |
| **Backend** | FastAPI + PostgreSQL: stores events, sessions, workers; broadcasts live state over WebSocket. |
| **Dashboard** | React + TypeScript + Vite: login, Live Overview (workers, alerts, KPIs, charts), Shift Summary (sessions), historical worker data. |

**Deployment:** All non-wearable components run on one laptop (no Raspberry Pi). PostgreSQL via Docker or local install.

---

## 2. System Architecture

### 2.1 High-Level Diagram

```
┌─────────────────────┐      BLE GATT       ┌─────────────────────┐     HTTP / WebSocket     ┌─────────────────────┐
│  Wearable (ESP32)   │ ──────────────────► │  Edge Gateway       │ ───────────────────────► │  Backend            │
│  MPU6050/9250, Temp │   JSON notify        │  Python (laptop)    │  POST /events, /sensor   │  FastAPI + Postgres  │
│  Worker ID: W01     │                      │  Buffer → ML → API  │  WS broadcast            │  JWT, WebSocket     │
└─────────────────────┘                      └─────────────────────┘                         └──────────┬──────────┘
                                                                                                          │
                                                                                                          ▼
                                                                                                 ┌─────────────────────┐
                                                                                                 │  Dashboard (React)  │
                                                                                                 │  Live View, Alerts  │
                                                                                                 │  Sessions, History  │
                                                                                                 └─────────────────────┘
```

### 2.2 Technology Stack

| Component | Technologies |
|-----------|--------------|
| **Firmware** | Arduino/PlatformIO, ESP32, Adafruit MPU6050, NimBLE, ArduinoJson |
| **Edge** | Python 3.10+, bleak (BLE), scikit-learn/joblib, aiohttp, numpy, pandas |
| **Backend** | FastAPI, SQLAlchemy (async), PostgreSQL (asyncpg), Alembic, JWT, WebSocket |
| **Dashboard** | React 19, TypeScript, Vite, Recharts, Framer Motion, Zustand, Axios |
| **ML** | scikit-learn, joblib (saved model); optional training in `ml/` |

### 2.3 Ports & URLs

| Service | Default URL/Port |
|---------|------------------|
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| WebSocket | ws://localhost:8000/ws/live |
| Dashboard | http://localhost:5173 |
| PostgreSQL | localhost:5432 (Docker or local install) |

---

## 3. What Was Built (by Component)

### 3.1 Firmware (ESP32)

- **Sketch:** `firmware/IndustrialWearableAI/IndustrialWearableAI.ino` (Arduino IDE) and/or PlatformIO under `firmware/`.
- **Behaviour:**
  - I2C init (SDA 21, SCL 22) with configurable delay and retries.
  - MPU6050 or MPU9250 (WHO_AM_I 0x68 or 0x70) init via Adafruit library (patched to accept 0x70).
  - Read accel/gyro at 25 Hz; pack JSON: `worker_id`, `ts`, `ax`, `ay`, `az`, `gx`, `gy`, `gz`, `temp` (temp placeholder if no sensor).
  - BLE GATT server (NimBLE): service/characteristic UUIDs; notify JSON on each sample.
  - When MPU not found: no fake IMU data; send device status `{ worker_id, mpu_connected: false }` every 2 s so dashboard can show “No MPU connected”.
- **Config:** `WORKER_ID` (e.g. W01), `MPU_I2C_ADDR` (0x68 or 0x69), `MPU_INIT_DELAY_MS`, `MPU_INIT_RETRIES`, BLE UUIDs.

### 3.2 Edge Gateway (Python)

- **Entry:** `edge/src/main.py` (`python -m src.main`).
- **Behaviour:**
  - Connect to wearable via BLE (or run in simulator if `BLE_DEVICE_ID` empty).
  - Ring buffer of raw samples; sliding window (e.g. 3 s @ 25 Hz); low-pass filter; 30-dim feature extraction (mean, std, min, max, zero-crossing per axis).
  - Classifier: loaded ML model (joblib) or rule-based (variance heuristic) → label: sewing, idle, adjusting, break, error.
  - Risk: `risk_ergo`, `risk_fatigue` (e.g. fatigue when idle).
  - Batch events and POST to `POST /api/events`; periodic flush; periodic sensor snapshot (temp, accel_mag) to `POST /api/live/sensor`.
  - When device reports `mpu_connected: false`, POST to `POST /api/live/device-status` and skip event buffering.
- **Key files:** `ble_client.py`, `buffer.py`, `pipeline.py`, `feature_extractor.py`, `classifier.py`, `api_client.py`.

### 3.3 Backend (FastAPI)

- **Entry:** `uvicorn app.main:app --reload`.
- **Database:** PostgreSQL; SQLAlchemy async; Alembic migrations. Models: User, Worker, Device, Session, SessionAggregate, ActivityEvent (and ActivityLabel enum).
- **Auth:** JWT (login, register, change-password, /auth/me).
- **APIs:**
  - **Events:** `POST /api/events` — accept batch of events, resolve/create worker and session, insert activity_events, update session_aggregates, broadcast worker state on WebSocket.
  - **Live:** `POST /api/live/sensor` (temp, accel_mag), `POST /api/live/device-status` (mpu_connected); broadcast to WebSocket clients.
  - **Workers:** `GET /api/workers`, `GET /api/workers/{worker_name}/history` (session history with aggregates).
  - **Sessions:** `GET /api/sessions`, `GET /api/sessions/{session_id}/summary`.
  - **Activity:** `GET /api/activity/timeline?from_ts=&to_ts=&bucket_minutes=` — bucketed activity for charts (historical).
- **WebSocket:** `/ws/live` — hub broadcasts worker state, sensor, device_status to dashboard.

### 3.4 Dashboard (React)

- **Entry:** `npm run dev` (Vite); default http://localhost:5173.
- **Auth:** Login page; JWT in localStorage; protected routes; optional change-password.
- **Pages:**
  - **Live Overview:** Real-time workers from WebSocket; KPIs (Live, Working, Idle, At Risk, Sample); Alerts panel; “Live now” section (live workers only) with sensor strip, tabs (All/Working/Idle/At risk), search/sort/filters, worker cards; “Sample workers” section (demo workers with historical data, expandable “View history”); Charts section (state donut, activity timeline with time-range selector, alerts trend).
  - **Shift Summary:** Sessions list and session summaries.
- **Components:** WorkerCard (state, badges, risk, sample/history), AlertsPanel, LiveSensorStrip, KpiCard, StateDonutLive, ActivityTimelineChart, AlertsTrendChart, Filters, EmptyState.
- **Data:** `useWebSocket` (workers, sensorByWorker, mpuConnectedByWorker, activityTimeline); `getWorkers()`, `getWorkerHistory(workerName)`, `getActivityTimeline(fromTs, toTs)`; merge API workers with live state for “live” vs “sample” split.

### 3.5 ML & Demo Data

- **ML:** Optional scikit-learn model in `ml/models/activity_model.joblib`; edge loads it or falls back to rule-based classifier. Feature pipeline matches training (30 features).
- **Demo workers:** `backend/seed_demo_workers.py` creates workers W01–W08 and 45 days of sessions/activity for W02–W08 for showcase; dashboard shows them as “Sample” with “View history” (session list with active_pct, idle_pct, alert_count).

---

## 4. Features Delivered

### 4.1 Live Overview (Showcase Phases A–D)

| Feature | Description |
|--------|-------------|
| **Tabs & filters** | All / Working / Idle / At risk with counts; search and sort for live workers. |
| **KPIs** | Live, Working, Idle, At Risk, Sample (with colored left bar on cards). |
| **Alerts panel** | All workers with risk_ergo or risk_fatigue; severity; last updated. |
| **Worker badges** | Working, Idle, At risk, Sample on each card; state pill (sewing, idle, etc.). |
| **State donut** | Current distribution of live workers by state. |
| **Activity timeline** | Stacked area chart; time range: Last 10 min (live), 1 h, 6 h, 24 h (historical API). |
| **Alerts trend** | Chart of at-risk events over last 10 min. |
| **Live sensor strip** | Temp and movement (accel_mag) per live worker from WebSocket. |
| **No MPU banner** | Shown when any live worker has device status `mpu_connected: false`. |
| **Toast on new alert** | When a worker becomes at risk, toast notification. |
| **Clear sections** | “Live now” (only live workers) vs “Sample workers” (historical demo) vs “Charts (live feed)”. |

### 4.2 Historical & Demo Data

- **Worker history API:** `GET /api/workers/{worker_name}/history` — list of sessions with started_at, ended_at, active_pct, idle_pct, adjusting_pct, error_pct, alert_count.
- **Activity timeline API:** `GET /api/activity/timeline` — bucketed counts by minute for past ranges (for chart).
- **Sample workers:** Seed script creates W02–W08 with 45 days of data; dashboard shows “Sample” badge and expandable “View history” with session list.

### 4.3 UI/UX

- **Colors:** KPI cards with colored left bar (teal/green/slate/red/gray); worker status badges (Working=green, Idle=slate, At risk=red, Sample=indigo); state pills with clear colors.
- **Responsive layout:** Grids and charts adapt; sections with headings and borders.
- **Empty states:** Clear messages when no workers or no live data; “No live feed” in Live now when only sample workers exist.

### 4.4 Classifier & “Working” vs “Idle”

- **Rule-based (no model):** Variance of accel/gyro std over window; thresholds tuned so normal sewing motion shows as sewing/adjusting, not idle. Per-axis check so one moving axis is enough to leave “idle”.
- **With model:** Edge loads joblib model; predicts label; same event format to backend.

---

## 5. Hardware & Firmware

### 5.1 Components

| Component | Spec |
|-----------|------|
| ESP32 | ESP32-WROOM-32 / DevKitC |
| IMU | MPU6050 (0x68) or MPU9250/clone (0x70) — 6-axis accel+gyro |
| Temp (optional) | DHT11 or DS18B20 |
| Power | Li-ion 3.7 V + TP4056 charger |

### 5.2 Wiring Summary

- **MPU:** VCC→3V3, GND→GND, SDA→GPIO21, SCL→GPIO22; AD0→GND for 0x68.
- **DHT11/DS18B20:** Data→GPIO4, VCC, GND (DS18B20: 4.7 kΩ pull-up).

Full tables and diagrams: **`docs/HARDWARE_CONNECTIONS.md`**.

### 5.3 Firmware Behaviour Summary

- Delay after I2C init (150 ms default) and retries (3) for MPU begin.
- Explicit I2C address (`MPU_I2C_ADDR` 0x68 or 0x69).
- Adafruit MPU6050 library **patched** to accept WHO_AM_I **0x70** (MPU9250) as well as 0x68 (MPU6050); patch in `.pio/libdeps/esp32dev/Adafruit MPU6050/Adafruit_MPU6050.cpp`.

### 5.4 BLE

- Service UUID: `0000fff0-...`; Characteristic UUID: `0000fff1-...` (notify).
- Edge connects by BLE address (`BLE_DEVICE_ID` in `edge/.env`); same UUIDs in `edge/src/ble_client.py`.

---

## 6. How to Run the Project

### 6.1 Prerequisites

- Python 3.10+ (backend, edge)
- Node.js 18+ (dashboard)
- PostgreSQL: Docker **or** local install (see below if Docker fails)

### 6.2 Run with Docker (PostgreSQL)

1. **Terminal 1 — Postgres:** `cd backend` → `docker compose up -d`; wait ~10 s.
2. **Terminal 2 — Backend:** `cd backend` → `.venv\Scripts\Activate.ps1` → `alembic upgrade head` → `python seed_user.py` → `python seed_demo_workers.py` → `uvicorn app.main:app --reload`.
3. **Terminal 3 — Edge:** `cd edge` → `.venv\Scripts\Activate.ps1` → `python -m src.main`.
4. **Terminal 4 — Dashboard:** `cd dashboard` → `npm install` → `npm run dev`.

First-time: create `.venv` and `pip install -r requirements.txt` in backend and edge.

### 6.3 Run without Docker (PostgreSQL on Windows)

If Docker gives “500 Internal Server Error” when pulling Postgres:

1. Install PostgreSQL from https://www.postgresql.org/download/windows/ (port 5432, set postgres password).
2. Create database: `CREATE DATABASE wearable_ai;`
3. In `backend/.env`: `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wearable_ai`
4. Skip Terminal 1; run Terminals 2–4 as above.

**Full step-by-step:** **`docs/RUN_COMMANDS.md`**.

### 6.4 Login & Demo

- Open http://localhost:5173 → Login: **admin** / **admin123** (run `python seed_user.py` if needed).
- With real hardware: set `edge/.env` → `BLE_DEVICE_ID=<ESP32_BLE_MAC>`, `WORKER_ID=W01`.
- Without hardware: leave `BLE_DEVICE_ID` empty; edge uses simulator and dashboard still updates.

---

## 7. APIs Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/login` | Login (JWT) |
| POST | `/api/auth/register` | Register |
| POST | `/api/auth/change-password` | Change password |
| GET | `/api/auth/me` | Current user (protected) |
| POST | `/api/events` | Event batch from edge (worker_id, events[]) |
| POST | `/api/live/sensor` | Sensor snapshot (worker_id, temp, accel_mag, ts) |
| POST | `/api/live/device-status` | Device status (worker_id, mpu_connected) |
| GET | `/api/workers` | List workers |
| GET | `/api/workers/{worker_name}/history` | Session history for worker |
| GET | `/api/sessions` | List sessions |
| GET | `/api/sessions/{session_id}/summary` | Session aggregate summary |
| GET | `/api/activity/timeline` | Bucketed activity (from_ts, to_ts, bucket_minutes) |
| WebSocket | `/ws/live` | Live state, sensor, device_status broadcasts |

---

## 8. Data Flow

| Stage | Data |
|-------|------|
| Wearable → Edge | JSON over BLE: `worker_id`, `ts`, `ax`, `ay`, `az`, `gx`, `gy`, `gz`, `temp` (or status-only if no MPU). |
| Edge → Backend | `POST /api/events`: `worker_id`, `events: [{ ts, label, risk_ergo, risk_fatigue }]`. `POST /api/live/sensor`: `worker_id`, `temp`, `accel_mag`, `ts`. `POST /api/live/device-status`: `worker_id`, `mpu_connected`. |
| Backend → Dashboard | WebSocket: worker state (`worker_id`, `name`, `current_state`, `risk_ergo`, `risk_fatigue`, `updated_at`); sensor (`worker_id`, `temp`, `accel_mag`, `ts`); device_status (`worker_id`, `mpu_connected`). |

**Activity labels:** sewing, idle, adjusting, break, error. **Risk flags:** risk_ergo, risk_fatigue.

---

## 9. Configuration

### 9.1 Backend (`backend/.env`)

- `DATABASE_URL` — PostgreSQL connection string.
- `SECRET_KEY` — JWT signing.
- `CORS_ORIGINS` — Allowed origins for dashboard.

### 9.2 Edge (`edge/.env`)

- `BACKEND_URL` — e.g. http://localhost:8000.
- `BLE_DEVICE_ID` — BLE MAC of ESP32 (empty = simulator).
- `WORKER_ID` — e.g. W01.
- `MODEL_PATH` — Optional path to joblib model (e.g. ml/models/activity_model.joblib).
- `WINDOW_SECONDS`, `OVERLAP` — Window and overlap for classifier.

### 9.3 Dashboard

- `VITE_API_URL` — Backend URL (e.g. http://localhost:8000).
- `VITE_WS_URL` — WebSocket URL (optional; defaults from API URL).

### 9.4 Firmware

- `WORKER_ID`, `SDA_PIN`, `SCL_PIN`, `MPU_I2C_ADDR`, `MPU_INIT_DELAY_MS`, `MPU_INIT_RETRIES`, BLE UUIDs (see `.ino`).

---

## 10. Troubleshooting

| Issue | What to do |
|-------|------------|
| **MPU6050 not found** | Increase `MPU_INIT_DELAY_MS` (e.g. 300–500); try `MPU_I2C_ADDR` 0x69; check wiring (SDA/SCL, 3V3, GND). See `docs/HARDWARE_CONNECTIONS.md`. |
| **WHO_AM_I = 0x70 / “chip not MPU6050”** | Board is MPU9250/clone. Adafruit library in this project is patched to accept 0x70; rebuild and upload. If you reinstall the library, re-apply the WHO_AM_I check to allow 0x70. |
| **Worker always shows Idle** | State comes from edge classifier. Lower thresholds in `edge/src/classifier.py` (`_rule_based_predict`) or use a trained model; ensure wearable is moving. See `docs/HARDWARE_CONNECTIONS.md` (Worker shows Idle). |
| **Docker 500 when pulling Postgres** | Use PostgreSQL on Windows; see “Run without Docker” in `docs/RUN_COMMANDS.md`. |
| **No workers / empty dashboard** | Ensure backend + edge + dashboard running; run `seed_user.py` and `seed_demo_workers.py`; check WebSocket (green “Connected”); with hardware set `BLE_DEVICE_ID`. |
| **Login fails** | Run `python backend/seed_user.py`; default admin/admin123. |

---

## 11. Related Documents

| Document | Purpose |
|----------|---------|
| **RUN_COMMANDS.md** | Step-by-step run commands (Docker + without Docker). |
| **RUN_ORDER.md** | Service startup order and first-run setup. |
| **HARDWARE_CONNECTIONS.md** | Wiring, pins, MPU not found, WHO_AM_I 0x70, Worker Idle. |
| **PROJECT_STATUS_AND_ARCHITECTURE.md** | Architecture and data flow detail. |
| **SHOWCASE_DASHBOARD_PLAN.md** | Plan for Live Overview (Phases A–D). |
| **SHOWCASE_STATUS.md** | What was delivered for showcase. |
| **TECHNICAL_STACK_SPEC.md** | API contracts and data formats. |
| **TESTING_WITHOUT_HARDWARE.md** | Test with simulator, no ESP32. |
| **PILOT_PREP.md** | Pilot deployment checklist. |
| **OVERALL_IDEA_SUMMARY.md** | Problem statement and high-level solution. |
| **MASTER_PLAN.md** | Implementation phases and checklists. |
| **RESEARCH_PAPER.md** | Full research paper (abstract, intro, related work, methodology, implementation, evaluation, discussion, conclusion, references). |
| **uml/README.md** | Index of UML diagrams (PlantUML); context, use case, component, deployment, sequence, class, activity, state. |

---

*This document is the single entry point for “what we did” in the Industrial Wearable AI project. For run commands and hardware details, use RUN_COMMANDS.md and HARDWARE_CONNECTIONS.md.*
