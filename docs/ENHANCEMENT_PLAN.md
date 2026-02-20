# Industrial Wearable AI — Comprehensive Enhancement Plan

> **Version:** 2.0  
> **Date:** 2026-02-20  
> **Objective:** Transform the MVP into a polished, competition-winning, production-grade product.  
> **Audience:** Developers executing this plan; hackathon/SIH judges; patent reviewers.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Vision (Enhanced)](#2-architecture-vision-enhanced)
3. [Phase 1 — Dashboard Excellence](#3-phase-1--dashboard-excellence)
4. [Phase 2 — Advanced AI/ML Intelligence](#4-phase-2--advanced-aiml-intelligence)
5. [Phase 3 — Backend Power-Ups](#5-phase-3--backend-power-ups)
6. [Phase 4 — Edge Gateway Hardening](#6-phase-4--edge-gateway-hardening)
7. [Phase 5 — Hardware & Firmware](#7-phase-5--hardware--firmware)
8. [Phase 6 — Analytics & Reports Engine](#8-phase-6--analytics--reports-engine)
9. [Phase 7 — Security, Privacy & Compliance](#9-phase-7--security-privacy--compliance)
10. [Phase 8 — Scale & Deployment](#10-phase-8--scale--deployment)
11. [Phase 9 — Integration Ecosystem](#11-phase-9--integration-ecosystem)
12. [Phase 10 — Innovation & Differentiators](#12-phase-10--innovation--differentiators)
13. [Implementation Timeline](#13-implementation-timeline)
14. [File & Folder Plan](#14-file--folder-plan)
15. [Competition Strategy Notes](#15-competition-strategy-notes)

---

## 1. Executive Summary

The current MVP delivers:
- ✅ ESP32 wearable → BLE → Edge gateway → FastAPI backend → PostgreSQL → React dashboard
- ✅ Activity classification (sewing, idle, adjusting, break, error)
- ✅ Ergonomic and fatigue risk detection
- ✅ Real-time WebSocket dashboard with worker cards, alerts, and charts
- ✅ Session history with aggregates
- ✅ Demo seed data (8 workers, 45 days of history)

**This plan adds 60+ enhancements across 10 phases** to create a polished, differentiated product that stands out in hackathons (SIH, Smart India, etc.), patent filings, research presentations, and investor demos.

---

## 2. Architecture Vision (Enhanced)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ENHANCED SYSTEM ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    BLE/WiFi    ┌──────────────────┐                  │
│  │  ESP32 Band   │──────────────▶│  Edge Gateway     │                  │
│  │  + MPU6050    │               │  + ML Inference   │                  │
│  │  + DHT11      │               │  + Offline Buffer │                  │
│  │  + MAX30102*  │               │  + Multi-device   │                  │
│  │  + Haptic*    │               │  + Feature Extract│                  │
│  └──────────────┘               └────────┬─────────┘                  │
│                                          │ REST + WS                    │
│                                          ▼                              │
│  ┌───────────────────────────────────────────────────────────────┐       │
│  │                     FastAPI Backend                            │      │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────┐  │      │
│  │  │ Auth &   │ │ Events & │ │ Analytics │ │ Notifications │  │      │
│  │  │ RBAC     │ │ Sessions │ │ Engine    │ │ Service       │  │      │
│  │  └──────────┘ └──────────┘ └───────────┘ └───────────────┘  │      │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────────┐  │      │
│  │  │ Config   │ │ Export/  │ │ Scheduler │ │ Audit Log     │  │      │
│  │  │ Service  │ │ Reports  │ │ (Celery)  │ │               │  │      │
│  │  └──────────┘ └──────────┘ └───────────┘ └───────────────┘  │      │
│  │                          │                                    │      │
│  │  ┌──────────┐  ┌────────┴──────┐  ┌───────────────┐         │      │
│  │  │PostgreSQL│  │ Redis (cache  │  │ S3/MinIO      │         │      │
│  │  │          │  │  + pub/sub)   │  │ (file export) │         │      │
│  │  └──────────┘  └───────────────┘  └───────────────┘         │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                          │ REST + WS                                    │
│                          ▼                                              │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │                    React Dashboard (Vite)                     │      │
│  │  ┌─────────────────────────────────────────────────────┐     │      │
│  │  │ Live View │ Analytics │ Reports │ Settings │ Admin  │     │      │
│  │  └─────────────────────────────────────────────────────┘     │      │
│  │  ┌─────────────────────────────────────────────────────┐     │      │
│  │  │  Floor Map │ Shift Replay │ Compare │ Notifications│     │      │
│  │  └─────────────────────────────────────────────────────┘     │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  * = Planned enhancement                                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phase 1 — Dashboard Excellence

> **Goal:** Make the dashboard visually stunning and feature-rich to immediately impress judges and users.

### 3.1 Analytics Page (NEW)

**File:** `dashboard/src/pages/Analytics.tsx` + `dashboard/src/pages/Analytics.css`

Create a dedicated analytics page that shows deep insights from historical data.

**Features:**
- **Productivity trend line** — daily/weekly active % per worker over time (line chart)
- **Heatmap grid** — rows = workers, columns = hours of day, color = activity intensity
- **Top/bottom performers** — ranked bar chart of workers by productivity score
- **State breakdown by worker** — stacked bar chart of sewing vs idle vs adjusting per worker
- **Time-of-day patterns** — when are workers most/least productive (area chart)
- **Risk frequency chart** — ergo/fatigue alerts per day per worker (heatmap)
- **Comparative analytics** — select 2 workers side-by-side, or 2 date ranges, or 2 shifts

**Backend endpoints needed:**
```
GET /api/analytics/productivity?from=&to=&worker_id=  → daily active %
GET /api/analytics/heatmap?from=&to=                  → worker × hour grid
GET /api/analytics/ranking?from=&to=&metric=           → ranked workers
GET /api/analytics/comparison?worker_a=&worker_b=&from=&to= → side-by-side
```

**Implementation steps:**
1. Create `backend/app/api/analytics.py` with 4 endpoints
2. Add SQL queries that aggregate `activity_events` by time bucket and worker
3. Create `dashboard/src/api/analytics.ts` API client
4. Build `Analytics.tsx` page with Recharts visualizations
5. Add route in `dashboard/src/App.tsx`
6. Add sidebar link in `dashboard/src/components/Sidebar.tsx`

---

### 3.2 Worker Profile Page (NEW)

**File:** `dashboard/src/pages/WorkerProfile.tsx` + `WorkerProfile.css`

Clicking a worker card navigates to `/workers/:id` showing a detailed profile.

**Features:**
- **Worker info header** — name, role, assigned device, current status badge
- **Activity timeline** — last 24h of state changes as a horizontal timeline
- **Shift history** — table of recent sessions with start/end, active %, alerts
- **Per-worker charts** — personal productivity trend, risk events, active hours
- **Quick actions** — assign/unassign device, change role, view alerts

**Implementation steps:**
1. Create `backend/app/api/workers.py` — `GET /api/workers/:id/profile` (stats + recent sessions)
2. Create `dashboard/src/pages/WorkerProfile.tsx`
3. Add route: `/workers/:id`
4. Update `WorkerCard.tsx` — make it clickable, navigate to profile

---

### 3.3 Settings Page (NEW)

**File:** `dashboard/src/pages/Settings.tsx` + `Settings.css`

**Features:**
- **Threshold configuration** — idle alert threshold (minutes), ergo angle limit, fatigue interval
- **Notification preferences** — toggle email/SMS/in-app alerts
- **Device management** — list of registered devices, BLE addresses, battery status
- **User management** — add/remove supervisors (admin only)
- **System info** — backend version, DB status, edge connection status

**Implementation steps:**
1. Create `backend/app/api/config.py` — CRUD for system config stored in `config` table
2. Create new DB table `system_config` with key-value pairs
3. Alembic migration for the new table
4. Create `dashboard/src/pages/Settings.tsx`
5. Add route and sidebar link

---

### 3.4 Shift Replay (NEW)

**File:** `dashboard/src/pages/ShiftReplay.tsx`

**Features:**
- **Playback slider** — scrub through a past shift, see worker states change over time
- **Speed control** — 1×, 2×, 5×, 10× playback
- **Timeline ruler** — events (state changes, alerts) plotted on a ruler
- **Worker cards** — show the state each worker was in at the selected timestamp

**Implementation steps:**
1. Create `backend/app/api/replay.py` — `GET /api/sessions/:id/replay` returns all events for a session
2. Build `ShiftReplay.tsx` with a time slider and animated worker cards
3. Add route: `/replay/:sessionId`

---

### 3.5 Dashboard UI Polish

**Files:** Various CSS and component files

| Enhancement | File(s) | Details |
|-------------|---------|---------|
| **Animated page transitions** | `App.tsx`, all pages | `framer-motion` `AnimatePresence` for route transitions |
| **Notification toast center** | `components/NotificationCenter.tsx` | Slide-in panel showing recent alerts with timestamps |
| **Loading skeletons everywhere** | `components/ui/Skeleton.tsx` | Consistent skeleton loading across all pages |
| **Keyboard shortcuts** | `hooks/useKeyboard.ts` | `Ctrl+1` = Live View, `Ctrl+2` = Sessions, `Ctrl+3` = Analytics, `?` = help |
| **Responsive mobile layout** | `Layout.css`, all pages | Hamburger menu on mobile, cards stack vertically, charts resize |
| **Print-friendly styles** | `print.css` | `@media print` styles for clean report printing |
| **Dark/light mode toggle** | `hooks/useTheme.ts`, `index.css` | CSS variables swap; saved in localStorage |
| **Connection indicator** | `components/ConnectionStatus.tsx` | Always-visible badge: 🟢 Connected, 🟡 Reconnecting, 🔴 Disconnected |
| **Onboarding walkthrough** | `components/Onboarding.tsx` | First-time user sees tooltip highlights on key UI elements |

---

## 4. Phase 2 — Advanced AI/ML Intelligence

> **Goal:** Make the AI layer impressive and unique — this is the core differentiator.

### 4.1 Multi-Model Inference Pipeline

**Files:** `ml/models/`, `edge/src/classifier.py`

**Current state:** Single RandomForest classifier for 5 activity states.

**Enhancement — 3-model pipeline:**

| Model | Input | Output | Tech |
|-------|-------|--------|------|
| **Activity Classifier** (exists) | 6-axis IMU (1s window) | sewing / idle / adjusting / break / error | RandomForest |
| **Fatigue Predictor** (NEW) | Rolling 10-min features: motion decay, repetition count, temp trend | Normal / Mild / High risk | Gradient Boosted Trees (XGBoost) |
| **Ergonomic Risk Scorer** (NEW) | Wrist angle (derived from accel), hold duration, repetition frequency | Score 0–100 → Low / Medium / High | Rules + logistic regression hybrid |

**Implementation steps:**
1. Create `ml/scripts/train_fatigue.py` — feature extraction from sessions, train XGBoost
2. Create `ml/scripts/train_ergo.py` — rule-based + ML hybrid
3. Export all 3 models as `.joblib` files to `ml/models/`
4. Update `edge/src/classifier.py` to load and run all 3 models
5. Update `edge/src/pipeline.py` — chain results: activity → fatigue check → ergo check
6. Update `backend/app/schemas.py` — add `fatigue_score`, `ergo_score` (numeric) to event payload
7. Update `dashboard` charts to show scores, not just boolean flags

### 4.2 Anomaly Detection

**File:** `ml/scripts/train_anomaly.py`, `edge/src/anomaly_detector.py`

**Features:**
- Use Isolation Forest or Local Outlier Factor on feature vectors
- Flag "unusual" windows: sudden stop after hours of activity, extreme temperature spikes
- Dashboard shows anomaly alerts separately from regular risk alerts

**Implementation steps:**
1. Train anomaly model on "normal" session features
2. Export as `.joblib`
3. Edge calls `anomaly_detector.predict()` on each feature window
4. Add `is_anomaly: bool` to event schema
5. Dashboard shows anomaly badge on worker card

### 4.3 Confidence Score + Active Learning

**Files:** `edge/src/classifier.py`, `dashboard/src/components/LabelingQueue.tsx`

**Features:**
- Classifier outputs probability per class; if max probability < 0.7, mark as "low confidence"
- Low-confidence windows pushed to a labeling queue in the dashboard
- Supervisor labels them (dropdown: sewing/idle/adjusting/break/error)
- Labels stored in DB; used to periodically retrain the model

**Implementation steps:**
1. Edge: use `model.predict_proba()` → send `confidence` field
2. Backend: `POST /api/labels` — save human label + link to event
3. Backend: `GET /api/labels/queue` — low-confidence events pending review
4. Dashboard: `LabelingQueue.tsx` page with event details + dropdown + submit
5. ML: `ml/scripts/retrain_with_labels.py` — merge human labels + original dataset, retrain

### 4.4 Per-Factory Calibration

**File:** `ml/scripts/calibrate.py`

**Features:**
- Fine-tune the activity model with 1–2 hours of labeled data from a specific factory
- Create factory-specific model files: `ml/models/activity_factory_001.joblib`
- Edge config: `MODEL_PATH=ml/models/activity_factory_001.joblib`

### 4.5 Productivity Score Algorithm

**File:** `backend/app/services/productivity.py`

**Formula:**
```python
productivity_score = (
    0.5 * active_ratio +           # fraction of time in sewing/adjusting
    0.2 * consistency_score +       # std deviation of activity (lower = more consistent)
    0.2 * (1 - risk_ratio) +        # fraction of time NOT in risk
    0.1 * (1 - break_excess)        # penalty for break time above threshold
) * 100
```

**Implementation steps:**
1. Create `backend/app/services/productivity.py` with the scoring function
2. Compute after each session aggregate update
3. Store in `session_aggregates.productivity_score`
4. Expose via `GET /api/analytics/productivity`
5. Dashboard shows score with color gradient (0–40 red, 40–70 yellow, 70–100 green)

---

## 5. Phase 3 — Backend Power-Ups

### 5.1 Role-Based Access Control (RBAC)

**Files:** `backend/app/models/user.py`, `backend/app/dependencies.py`, `backend/app/api/auth.py`

**Roles:**
| Role | Permissions |
|------|------------|
| `SUPER_ADMIN` | Everything: manage tenants, users, global config |
| `FACTORY_ADMIN` | Manage workers, view all data, configure thresholds |
| `SUPERVISOR` | View live data, view reports, label events |
| `VIEWER` | View-only access to dashboard |

**Implementation steps:**
1. Add `role` column to `User` model: `role = Column(Enum('super_admin', 'factory_admin', 'supervisor', 'viewer'))`
2. Create dependency `require_role(*roles)` in `dependencies.py`
3. Apply to endpoints: admin-only for user management, supervisor+ for labeling, viewer+ for read
4. Dashboard: hide admin UI elements for non-admin users
5. Alembic migration for the role column

### 5.2 Notifications Service

**File:** `backend/app/services/notifications.py`

**Features:**
- In-app notifications stored in `notifications` table
- Email alerts via SMTP (configurable)
- Notification preferences per user
- WebSocket push for real-time in-app alerts

**Implementation steps:**
1. Create `notifications` table: id, user_id, type, title, body, read, created_at
2. Create `backend/app/services/notifications.py` — create, send, mark-read
3. Create `backend/app/api/notifications.py` — GET (list), PATCH (mark read)
4. Dashboard: `NotificationCenter.tsx` component with bell icon + unread count
5. Email: use `fastapi-mail` or `aiosmtplib` for SMTP

### 5.3 Bulk Data Export

**File:** `backend/app/api/export.py`

**Features:**
- Export sessions, events, or analytics as CSV or Excel (`.xlsx`)
- Filter by date range, worker, state
- Background job for large exports (Celery + Redis)
- Download link sent via notification when ready

**Implementation steps:**
1. Install `openpyxl` for Excel generation
2. Create `backend/app/api/export.py` with endpoints:
   - `POST /api/export/sessions` — start export job
   - `GET /api/export/:job_id` — download file
3. Store generated files in `exports/` directory (or S3/MinIO in production)
4. Dashboard: export button on Sessions and Analytics pages

### 5.4 Configurable Thresholds

**File:** `backend/app/api/config.py`, new table `system_config`

**Features:**
- Store all thresholds in DB instead of hardcoded: idle alert (min), ergo angle, fatigue interval, break reminder (min)
- Admin can change via dashboard settings page
- Edge fetches config on startup and periodically: `GET /api/config/thresholds`

**Implementation steps:**
1. Create `system_config` table: key (string), value (JSON), updated_at
2. Seed defaults on first run
3. Create CRUD endpoints
4. Edge: fetch on startup → apply to pipeline
5. Dashboard: Settings page with form inputs + save button

### 5.5 Audit Log

**File:** `backend/app/services/audit.py`, new table `audit_log`

**Features:**
- Log every significant action: login, config change, export, user create/delete
- Fields: who, what action, on what resource, when, IP address
- Viewable by SUPER_ADMIN in dashboard

---

## 6. Phase 4 — Edge Gateway Hardening

### 6.1 Multi-Device BLE Manager

**File:** `edge/src/ble_manager.py`

**Current state:** Single BLE device connection.

**Enhancement:**
- Connect to 5–10 ESP32 wearables simultaneously
- Each device maps to a worker_id
- Device registry: `edge/devices.json` — list of `{ble_address, worker_id}`
- Auto-reconnect on disconnect per device
- Dashboard shows per-device connection status

**Implementation steps:**
1. Create `edge/src/ble_manager.py` — `BLEDeviceManager` class with `add_device()`, `connect_all()`, `disconnect_all()`
2. Each device runs in its own async task
3. Update `edge/src/main.py` to use the manager
4. Create `edge/devices.json` config file
5. Edge reports per-device status to backend: `POST /api/live/device-status`

### 6.2 Offline Mode with Sync

**File:** `edge/src/offline_buffer.py`

**Features:**
- When backend is unreachable, store events in local SQLite: `edge/offline.db`
- On reconnection, batch-sync all buffered events (FIFO)
- Dashboard shows "Edge offline — N events buffered" status

**Implementation steps:**
1. Create `edge/src/offline_buffer.py` — SQLite-backed queue
2. Wrap `api_client.post_events()` — try backend first, fallback to buffer
3. Background task: periodically check backend health, drain buffer when available
4. Edge WebSocket or status API to report buffer depth

### 6.3 Edge Health API

**File:** `edge/src/health_server.py`

**Features:**
- Simple HTTP server on port 8081: `GET /status`
- Returns: uptime, connected devices, buffer depth, model loaded, backend reachable
- Backend periodically polls this (or edge pushes heartbeat)
- Dashboard shows edge health card

---

## 7. Phase 5 — Hardware & Firmware

### 7.1 Complete ESP32 Firmware

**File:** `firmware/src/main.cpp` (or `.ino`)

**Current state:** Firmware is a placeholder; not yet implemented.

**Full firmware implementation:**
```
firmware/
├── src/
│   ├── main.cpp              # Setup + loop
│   ├── sensors/
│   │   ├── mpu6050.cpp/.h    # IMU read (I2C)
│   │   ├── dht11.cpp/.h      # Temperature + humidity
│   │   └── ds18b20.cpp/.h    # Body temperature
│   ├── ble/
│   │   ├── ble_server.cpp/.h # GATT server with characteristics
│   │   └── config.h          # UUIDs, service name
│   ├── power/
│   │   ├── battery.cpp/.h    # ADC reading for battery %
│   │   └── sleep.cpp/.h      # Deep sleep, wake on motion
│   └── config.h              # Pin definitions, sampling rate
├── platformio.ini            # Build config
└── README.md                 # Wiring guide
```

**BLE GATT characteristics:**
| Characteristic | UUID | Data |
|---------------|------|------|
| Sensor Data | `0x0001` | JSON: `{ax, ay, az, gx, gy, gz, temp, humidity}` |
| Battery Level | `0x0002` | `{battery_pct: 85}` |
| Device Info | `0x0003` | `{firmware_version, uptime_sec, mpu_connected}` |
| Config (write) | `0x0004` | `{sample_rate_hz: 25}` (written by edge) |

### 7.2 Haptic Feedback

**Hardware:** Small vibration motor (coin type) connected to ESP32 GPIO

**Logic:**
- Edge sends risk alert message to firmware via BLE write characteristic
- Firmware vibrates motor: 2 short pulses = ergo risk, 1 long pulse = fatigue
- Worker feels alert without needing to look at any screen

### 7.3 LED Status Indicator

**Hardware:** WS2812 or simple RGB LED on the band

**States:**
| Color | Meaning |
|-------|---------|
| 🟢 Green steady | Connected, normal |
| 🟡 Yellow blink | Connected, mild risk |
| 🔴 Red blink | Disconnected or high risk |
| 🔵 Blue pulse | Pairing mode |

### 7.4 Battery Level Reporting

**Implementation:**
1. ADC read on battery voltage divider
2. Map to 0–100% using discharge curve
3. Send in BLE `battery` characteristic every 60s
4. Edge forwards to backend: `POST /api/live/battery`
5. Dashboard shows battery icon on worker card with color (green/yellow/red)

---

## 8. Phase 6 — Analytics & Reports Engine

### 8.1 PDF Report Generator

**File:** `backend/app/services/report_generator.py`

**Features:**
- Generate formatted PDF reports for any date range
- Includes: summary stats, charts (as images), worker performance table, risk log
- Use `reportlab` or `weasyprint` for PDF generation
- Triggered manually (dashboard button) or scheduled (daily/weekly)

**Report template:**
```
╔═══════════════════════════════════════════════╗
║     Industrial Wearable AI — Shift Report      ║
║     Date: 2026-02-20 | Shift: Day (6AM-2PM)   ║
╠═══════════════════════════════════════════════╣
║ Workers active:    8                           ║
║ Avg productivity:  73%                         ║
║ Total alerts:      12 (3 ergo, 9 fatigue)     ║
║ Top performer:     W03 (89%)                   ║
╠═══════════════════════════════════════════════╣
║ [Productivity Chart — bar chart]               ║
║ [Alert Trend — line chart]                     ║
║ [Per-Worker Breakdown — table]                 ║
╚═══════════════════════════════════════════════╝
```

### 8.2 Scheduled Reports (Celery)

**Files:** `backend/app/tasks/`, `backend/celery_config.py`

**Features:**
- Daily shift summary → email to supervisor at end of shift
- Weekly digest → email to factory admin on Monday morning
- Use Celery + Redis for background task scheduling
- Configurable via Settings page

### 8.3 Root-Cause Analytics

**File:** `backend/app/services/root_cause.py`

**Features:**
- Correlate idle % with: humidity, temperature, time of day, day of week
- Generate insights: "Station 4 has 30% higher idle when humidity > 70%"
- Use simple regression or correlation analysis
- Show as "Insights" cards on the Analytics page

---

## 9. Phase 7 — Security, Privacy & Compliance

### 9.1 Security Hardening

| Item | Implementation |
|------|---------------|
| **Password hashing upgrade** | Migrate from bcrypt to Argon2id (gold standard) |
| **Rate limiting** | `slowapi` middleware: 100 req/min per IP for API, 5/min for login |
| **HTTPS enforcement** | Redirect HTTP → HTTPS; HSTS header |
| **API key for edge** | Edge authenticates with API key header; rotate keys via admin |
| **Input validation** | Pydantic models for all endpoints (already exists); add size limits |
| **CORS tightening** | Restrict to known dashboard origins only (not `*`) |
| **JWT refresh tokens** | Short-lived access tokens (15 min) + refresh tokens (7 days) |
| **Session invalidation** | Logout invalidates token; stored in Redis blacklist |

### 9.2 Privacy & Consent

**Files:** `backend/app/models/consent.py`, `dashboard/src/pages/Privacy.tsx`

**Features:**
- Worker consent form before data collection begins
- Consent record stored: `worker_id, consented_at, ip, purpose, expiry`
- Data anonymization: after configurable retention period, replace worker name with hash
- Right to deletion: admin can purge all data for a worker
- Privacy policy page in dashboard

### 9.3 Compliance Reports

**File:** `backend/app/services/compliance.py`

**Features:**
- ISO 45001 aligned safety metrics
- "Hours at risk" per worker per month
- "Ergo alerts per worker" — trend over time
- "Break compliance" — did workers take mandatory breaks?
- Exportable as PDF for auditors

---

## 10. Phase 8 — Scale & Deployment

### 10.1 Docker Compose (Full Stack)

**File:** `docker-compose.yml` (root level)

```yaml
services:
  postgres:
    image: postgres:15-alpine
    volumes: [pgdata:/var/lib/postgresql/data]
    environment: { POSTGRES_DB: wearable_ai, ... }
  
  redis:
    image: redis:7-alpine
  
  backend:
    build: ./backend
    depends_on: [postgres, redis]
    ports: ["8000:8000"]
  
  celery-worker:
    build: ./backend
    command: celery -A celery_config worker
    depends_on: [redis]
  
  celery-beat:
    build: ./backend
    command: celery -A celery_config beat
    depends_on: [redis]
  
  dashboard:
    build: ./dashboard
    ports: ["80:80"]

volumes:
  pgdata:
```

### 10.2 Dockerfiles

**Files:** `backend/Dockerfile`, `dashboard/Dockerfile`

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# dashboard/Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### 10.3 CI/CD Pipeline

**File:** `.github/workflows/ci.yml`

**Steps:**
1. **Lint + Type Check** — ESLint + tsc -b for dashboard, flake8/mypy for backend
2. **Unit Tests** — pytest for backend, vitest for dashboard
3. **Build** — Docker images for backend + dashboard
4. **Deploy** — Push to container registry; deploy to staging

---

## 11. Phase 9 — Integration Ecosystem

### 11.1 Webhook System

**File:** `backend/app/services/webhooks.py`

**Features:**
- Admin registers webhook URLs: `POST /api/webhooks` with URL + events filter
- On matching event (alert, session_end, anomaly), POST JSON to webhook URL
- Retry with exponential backoff on failure
- Use cases: Slack alerts, email via Zapier, ERP sync

### 11.2 Slack Integration

**File:** `backend/app/integrations/slack.py`

**Features:**
- Configure Slack incoming webhook URL in Settings
- On ergo/fatigue alert: post to Slack channel with worker name, risk type, timestamp
- Optional: rich Slack blocks with action buttons ("View in dashboard", "Dismiss")

### 11.3 Email Alerts

**File:** `backend/app/services/email.py`

**Features:**
- SMTP configuration in Settings
- Email templates (HTML) for: alert, daily summary, weekly digest
- Configurable recipients per notification type

### 11.4 REST API for Partners

**File:** `backend/app/api/partner.py`

**Features:**
- API key authenticated endpoints for third-party integrations
- `GET /api/v1/workers` — list workers
- `GET /api/v1/sessions` — list sessions with aggregates
- `GET /api/v1/events` — stream events by date range
- Rate limited separately from internal dashboard API
- Versioned: `/api/v1/`

---

## 12. Phase 10 — Innovation & Differentiators

> **These are the "wow factor" features that set this apart from any competing system.**

### 12.1 Digital Twin Visualization

**File:** `dashboard/src/components/DigitalTwin.tsx`

**Features:**
- 3D or 2D animated figure showing worker posture in real-time
- Wrist position derived from IMU angles
- Color codes limbs by risk level (green → red)
- Use Three.js or a simple SVG animation
- Updated in real-time via WebSocket data

**Why it matters:** This is a *patent-grade* visual differentiator. Judges immediately understand the value.

### 12.2 Floor Map View

**File:** `dashboard/src/pages/FloorMap.tsx`

**Features:**
- Upload factory floor plan image
- Drag-and-drop worker locations onto the map
- Workers show as color-coded dots (green = working, red = at risk, gray = idle)
- Click dot → opens worker card overlay
- Powered by canvas or SVG overlay

### 12.3 Voice Alerts (Text-to-Speech)

**File:** `dashboard/src/hooks/useVoiceAlert.ts`

**Features:**
- When a new at-risk worker is detected, play audio alert: "Worker W03, fatigue risk detected"
- Use Web Speech API (`SpeechSynthesisUtterance`)
- Configurable: enable/disable in Settings
- Useful for factory supervisors who aren't looking at the screen

### 12.4 Predictive Maintenance Insight

**File:** `backend/app/services/predictive.py`

**Features:**
- "Worker W05 is likely to be fatigued in 30 minutes based on current pattern"
- Uses rolling window comparison with historical patterns for same worker
- Display as a warning card on LiveView before the risk actually triggers
- Shows estimated time-to-fatigue

### 12.5 Shift Comparison Dashboard

**File:** `dashboard/src/pages/ShiftCompare.tsx`

**Features:**
- Compare two shifts side-by-side: morning vs afternoon, today vs yesterday
- Metrics: total productivity, alert count, top performer, worst bottleneck
- Visual diff: green for improvement, red for decline

### 12.6 Gamification & Leaderboard

**File:** `dashboard/src/components/Leaderboard.tsx`

**Features:**
- Optional weekly leaderboard: top 5 workers by productivity score
- Badges: "Streak" (5 days no risk), "Star" (90%+ productivity), "New record"
- Animated card reveal with confetti effect 🎉
- Toggle on/off in Settings (privacy-sensitive)

### 12.7 Natural Language Query (AI Chat)

**File:** `dashboard/src/components/AIChat.tsx`, `backend/app/api/nl_query.py`

**Features:**
- Chat box: "Show me workers who were idle for more than 30 min today"
- Backend parses natural language → SQL query → returns results
- Use a simple rule-based parser (no LLM needed for common queries)
- Alternative: integrate with a local LLM for complex queries (Ollama/llama.cpp)

### 12.8 Multi-Language Support (i18n)

**File:** `dashboard/src/i18n/`, `dashboard/src/hooks/useTranslation.ts`

**Languages:** English, Hindi (for textile SMEs in India)

**Implementation:**
1. Create `dashboard/src/i18n/en.json` and `dashboard/src/i18n/hi.json` translation files
2. Create `useTranslation` hook that reads from JSON based on locale
3. Replace all hardcoded strings with `t('key')` calls
4. Language selector in Settings page

---

## 13. Implementation Timeline

| Week | Phase | Key Deliverables |
|------|-------|------------------|
| **Week 1** | Phase 1 (Dashboard) | Analytics page, Worker Profile, Settings page |
| **Week 2** | Phase 1 (Dashboard) | Shift Replay, dark mode, mobile responsive, UI polish |
| **Week 3** | Phase 2 (AI/ML) | Fatigue predictor, ergo scorer, anomaly detection |
| **Week 4** | Phase 2 (AI/ML) | Confidence scores, labeling queue, productivity score |
| **Week 5** | Phase 3 (Backend) | RBAC, notifications, bulk export, configurable thresholds |
| **Week 6** | Phase 4 (Edge) | Multi-device BLE, offline mode, edge health API |
| **Week 7** | Phase 5 (Firmware) | Complete ESP32 firmware, battery reporting, LED status |
| **Week 8** | Phase 6 (Reports) | PDF generator, scheduled reports, root-cause analytics |
| **Week 9** | Phase 7 (Security) | RBAC enforcement, rate limiting, consent system |
| **Week 10** | Phase 8 (Deploy) | Docker Compose, Dockerfiles, CI/CD pipeline |
| **Week 11** | Phase 9 (Integrations) | Webhooks, Slack, email alerts |
| **Week 12** | Phase 10 (Innovation) | Digital twin, floor map, voice alerts, AI chat |

**For competitions/demos (minimum viable "wow" set — 2 weeks):**
- ✅ Analytics page (Phase 1)
- ✅ Digital twin visualization (Phase 10)
- ✅ Floor map view (Phase 10)
- ✅ PDF report (Phase 6)
- ✅ Dark mode + mobile responsive (Phase 1)
- ✅ Productivity score (Phase 2)
- ✅ Voice alerts (Phase 10)

---

## 14. File & Folder Plan

### New Backend Files
```
backend/
├── app/
│   ├── api/
│   │   ├── analytics.py          # [NEW] Analytics endpoints
│   │   ├── config.py             # [NEW] Config CRUD
│   │   ├── export.py             # [NEW] CSV/Excel export
│   │   ├── notifications.py      # [NEW] Notification endpoints
│   │   ├── partner.py            # [NEW] Partner API v1
│   │   ├── replay.py             # [NEW] Shift replay
│   │   └── nl_query.py           # [NEW] Natural language query
│   ├── models/
│   │   ├── config.py             # [NEW] SystemConfig model
│   │   ├── notification.py       # [NEW] Notification model
│   │   ├── consent.py            # [NEW] Consent model
│   │   └── audit_log.py          # [NEW] AuditLog model
│   ├── services/
│   │   ├── notifications.py      # [NEW] Notification logic
│   │   ├── productivity.py       # [NEW] Productivity score
│   │   ├── report_generator.py   # [NEW] PDF report
│   │   ├── root_cause.py         # [NEW] Root-cause analytics
│   │   ├── compliance.py         # [NEW] Compliance reports
│   │   ├── predictive.py         # [NEW] Predictive fatigue
│   │   ├── audit.py              # [NEW] Audit logging
│   │   ├── webhooks.py           # [NEW] Webhook dispatch
│   │   └── email.py              # [NEW] Email service
│   ├── integrations/
│   │   └── slack.py              # [NEW] Slack integration
│   └── tasks/
│       ├── __init__.py           # [NEW] Celery tasks
│       ├── report_tasks.py       # [NEW] Scheduled reports
│       └── sync_tasks.py         # [NEW] Data sync tasks
├── celery_config.py              # [NEW] Celery configuration
├── Dockerfile                    # [NEW] Docker build
└── alembic/versions/
    ├── xxx_add_system_config.py  # [NEW] Migration
    ├── xxx_add_notifications.py  # [NEW] Migration
    ├── xxx_add_audit_log.py      # [NEW] Migration
    ├── xxx_add_consent.py        # [NEW] Migration
    └── xxx_add_user_role.py      # [NEW] Migration
```

### New Dashboard Files
```
dashboard/
├── src/
│   ├── pages/
│   │   ├── Analytics.tsx         # [NEW] Analytics page
│   │   ├── Analytics.css         # [NEW]
│   │   ├── WorkerProfile.tsx     # [NEW] Worker detail page
│   │   ├── WorkerProfile.css     # [NEW]
│   │   ├── Settings.tsx          # [NEW] Settings page
│   │   ├── Settings.css          # [NEW]
│   │   ├── ShiftReplay.tsx       # [NEW] Shift replay page
│   │   ├── FloorMap.tsx          # [NEW] Factory floor map
│   │   ├── FloorMap.css          # [NEW]
│   │   └── ShiftCompare.tsx      # [NEW] Shift comparison
│   ├── components/
│   │   ├── DigitalTwin.tsx       # [NEW] 3D/2D posture viz
│   │   ├── Leaderboard.tsx       # [NEW] Weekly leaderboard
│   │   ├── AIChat.tsx            # [NEW] NL query interface
│   │   ├── NotificationCenter.tsx# [NEW] Notification panel
│   │   ├── ConnectionStatus.tsx  # [NEW] WS status badge
│   │   ├── Onboarding.tsx        # [NEW] First-run walkthrough
│   │   └── charts/
│   │       ├── ProductivityChart.tsx    # [NEW]
│   │       ├── HeatmapChart.tsx         # [NEW]
│   │       └── ComparisonChart.tsx      # [NEW]
│   ├── hooks/
│   │   ├── useTheme.ts           # [NEW] Dark/light toggle
│   │   ├── useKeyboard.ts        # [NEW] Keyboard shortcuts
│   │   ├── useVoiceAlert.ts      # [NEW] TTS alerts
│   │   └── useTranslation.ts     # [NEW] i18n hook
│   ├── api/
│   │   ├── analytics.ts          # [NEW] Analytics API
│   │   ├── config.ts             # [NEW] Config API
│   │   ├── export.ts             # [NEW] Export API
│   │   └── notifications.ts      # [NEW] Notifications API
│   ├── i18n/
│   │   ├── en.json               # [NEW] English strings
│   │   └── hi.json               # [NEW] Hindi strings
│   └── print.css                 # [NEW] Print styles
├── Dockerfile                    # [NEW] Docker build
└── nginx.conf                    # [NEW] Nginx config
```

### New Edge Files
```
edge/
├── src/
│   ├── ble_manager.py            # [NEW] Multi-device BLE
│   ├── offline_buffer.py         # [NEW] SQLite offline queue
│   ├── health_server.py          # [NEW] Edge health HTTP
│   └── anomaly_detector.py       # [NEW] Anomaly detection
├── devices.json                  # [NEW] Device registry
└── Dockerfile                    # [NEW] Docker build
```

### New ML Files
```
ml/
├── scripts/
│   ├── train_fatigue.py          # [NEW] Fatigue model
│   ├── train_ergo.py             # [NEW] Ergo risk model
│   ├── train_anomaly.py          # [NEW] Anomaly detector
│   ├── calibrate.py              # [NEW] Per-factory calibration
│   └── retrain_with_labels.py    # [NEW] Active learning retrain
└── models/
    ├── fatigue_model.joblib      # [NEW] Trained fatigue model
    ├── ergo_model.joblib         # [NEW] Trained ergo model
    └── anomaly_model.joblib      # [NEW] Trained anomaly model
```

### Root Files
```
./
├── docker-compose.yml            # [NEW] Full-stack compose
├── .github/workflows/ci.yml     # [NEW] CI/CD pipeline
└── run.py                        # [EXISTS] Updated with new services
```

---

## 15. Competition Strategy Notes

### What Judges Look For

| Criteria | How We Score |
|----------|-------------|
| **Innovation** | Digital twin, predictive fatigue, active learning, NL query — unique to this system |
| **Completeness** | End-to-end: hardware → firmware → edge → backend → dashboard → analytics → reports |
| **Technical depth** | 3-model ML pipeline, WebSocket real-time, RBAC, async Python, TypeScript React |
| **Impact** | Quantifiable: "reduced idle time by X%", "prevented Y ergo risk events" |
| **Scalability** | Docker Compose, multi-tenant, cloud-ready, multi-site |
| **UI/UX** | Dark mode, animations, floor map, digital twin, voice alerts — polished |
| **Documentation** | This file + existing 26 markdown docs + UML diagrams + research paper |

### Demo Script (5 minutes)

1. **Opening (30s):** Problem statement — human-machine invisibility in textile SMEs
2. **Architecture (30s):** Show system diagram, explain 5 layers
3. **Live demo (2 min):**
   - Show dashboard with 8 workers in real-time
   - Click worker → profile page with history
   - Show analytics page with heatmap and trends
   - Trigger a risk alert → see toast + voice alert
   - Show digital twin reacting to worker motion
4. **AI/ML depth (1 min):** Explain 3-model pipeline, confidence scores, labeling queue
5. **Impact + scale (30s):** Cost (₹1500/band), multi-site, cloud-ready, 80+ enhancements planned
6. **Close (30s):** Patent potential, startup viability, "digital twins of the human workforce"

### Key Differentiators to Emphasize

1. **Low-cost** — ₹1,500 per wearable (vs ₹50,000+ for commercial solutions)
2. **Edge AI** — ML inference at the gateway, not in the cloud (low latency, works offline)
3. **Human-centric** — designed for worker safety, not surveillance
4. **Industry 4.0 for SMEs** — democratizing factory intelligence for small manufacturers
5. **Modular** — any textile role (sewing, cutting, packing) with same hardware
6. **Full-stack** — complete end-to-end system, not a prototype or concept

---

> **This document is the single source of truth for all enhancements.** Each phase can be executed independently. Features are ordered by impact-to-effort ratio within each phase. For competitions, prioritize Phase 1 (Dashboard) + Phase 2 (AI/ML) + Phase 10 (Innovation) for maximum visual impact.
