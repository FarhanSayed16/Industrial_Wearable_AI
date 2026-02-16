# Industrial Wearable AI — Project Status & Architecture

**Document:** Complete overview of what’s left, what to configure, and how the system works.  
**Version:** 1.0  
**Last updated:** 2025-02-04

---

## Table of Contents

1. [What’s Left in the Project](#1-whats-left-in-the-project)
2. [IoT / Component Parts to Configure Manually](#2-iot--component-parts-to-configure-manually)
3. [Exact Architecture](#3-exact-architecture)
4. [How It Works (Step-by-Step)](#4-how-it-works-step-by-step)
5. [Data Flow Summary](#5-data-flow-summary)
6. [Current Modes (Without Hardware)](#6-current-modes-without-hardware)

---

## 1. What’s Left in the Project

All software phases are complete. The only remaining work is hardware-related:

| Item | Status | Notes |
|------|--------|------|
| **ESP32 firmware** | Placeholder only | `firmware/src/main.cpp` is a stub; replace with full implementation when hardware is ready |
| **Default admin password** | Must change before pilot | Run `python backend/change_password.py admin` before deployment |

Everything else (backend, edge, dashboard, ML pipeline, simulator) is implemented and integrated.

---

## 2. IoT / Component Parts to Configure Manually

### 2.1 Hardware (Buy & Assemble)

| Component | Specification | Configuration Notes |
|-----------|---------------|---------------------|
| **ESP32** | ESP32-WROOM-32 / DevKitC | Flash firmware via PlatformIO |
| **MPU6050** | 6-axis IMU, I2C address 0x68 | Wire SDA, SCL, VCC, GND to ESP32 |
| **Temperature sensor** | DHT11 or DS18B20 | Choose one; wire per datasheet |
| **Battery** | Li-ion 3.7V 500–1000 mAh + TP4056 | Power + USB charging |
| **Wrist band / enclosure** | Strap + case | Mount PCB; keep temp sensor ventilated |

**Wiring (indicator):**

- MPU6050: SDA → ESP32 GPIO21, SCL → GPIO22, VCC → 3.3V, GND → GND
- DHT11: Data → GPIO4, VCC → 3.3V, GND → GND
- DS18B20: Data → GPIO4 (with 4.7k pull-up), VCC, GND

### 2.2 Software / Firmware Configuration

| Component | What to Configure |
|-----------|-------------------|
| **Firmware** | Worker ID (e.g. in NVS or compile-time) |
| **Firmware** | BLE GATT UUID for notify (must match edge) |
| **Edge** | `BLE_DEVICE_ID` in `edge/.env` — BLE MAC address of the wearable |
| **Edge** | `WORKER_ID` — unique per device (W01, W02, …) |
| **Backend** | `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS` (see `PILOT_PREP.md`) |

### 2.3 BLE Wiring (Wearable ↔ Edge)

| Step | Action |
|------|--------|
| 1 | Build ESP32 firmware; define GATT characteristic UUID |
| 2 | Update `CHAR_UUID` in `edge/src/ble_client.py` (line ~77) to match firmware |
| 3 | Set `BLE_DEVICE_ID` in `edge/.env` to the wearable’s BLE MAC address |

### 2.4 Firmware Implementation Tasks (When Hardware Ready)

From `firmware/README.md`:

1. Initialize I2C, MPU6050, temp sensor
2. Read IMU at 25–50 Hz
3. Read temp at 0.2–1 Hz
4. Pack JSON with ArduinoJson
5. Advertise BLE service; send via GATT
6. Store `worker_id` in NVS or compile-time

---

## 3. Exact Architecture

### 3.1 High-Level System Diagram

```
┌─────────────────┐     BLE / WiFi      ┌──────────────────┐     HTTP/WS      ┌─────────────────┐
│  Wearable Node  │ ──────────────────► │  Edge Gateway    │ ─────────────────► │  Backend + DB   │
│  (ESP32+IMU+Temp)│                     │  (Laptop)        │                   │  (API + ML)     │
└─────────────────┘                     └──────────────────┘                   └────────┬────────┘
                                                                                         │
                                                                                         ▼
                                                                                ┌─────────────────┐
                                                                                │  Web Dashboard   │
                                                                                │  (React)        │
                                                                                └─────────────────┘
```

### 3.2 Deployment (Laptop Only)

| Service | Runs On | Port |
|---------|---------|------|
| PostgreSQL | Laptop (Docker) | 5432 |
| Backend (FastAPI) | Laptop | 8000 |
| Edge (Python) | Laptop | — |
| Dashboard (React/Vite) | Laptop (dev server) | 5173 |

**No Raspberry Pi.** All components run on one laptop.

### 3.3 Component Stack

| Component | Technology |
|-----------|------------|
| Wearable | ESP32, MPU6050, DHT11/DS18B20, BLE |
| Edge | Python 3.10+, bleak, scikit-learn, aiohttp |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, WebSocket |
| Dashboard | React, TypeScript, Vite |
| ML | scikit-learn, joblib |

### 3.4 Network & Connectivity

| Link | Technology | Range / Notes |
|------|------------|---------------|
| Wearable ↔ Edge | BLE 4.2 (GATT) | ~10 m indoor; one wearable per connection |
| Edge ↔ Backend | HTTP/1.1 | LAN; same subnet |
| Dashboard ↔ Backend | HTTP, WebSocket | Browser; same network |

---

## 4. How It Works (Step-by-Step)

### 4.1 Wearable (ESP32)

1. Read MPU6050 (ax, ay, az, gx, gy, gz) at ~25 Hz
2. Read temp at ~0.2–1 Hz
3. Pack JSON: `{worker_id, ts, ax, ay, az, gx, gy, gz, temp}`
4. Send via BLE GATT notify

**Expected JSON payload (per TECHNICAL_STACK_SPEC §4.1):**

```json
{
  "worker_id": "W01",
  "ts": 1704067200123,
  "ax": -0.3, "ay": 1.2, "az": 9.6,
  "gx": 21, "gy": -4, "gz": 3,
  "temp": 31.5
}
```

### 4.2 Edge Gateway (Laptop)

1. Connect to wearable via BLE (or run simulator if no device)
2. Buffer samples in a ring buffer
3. Extract windows (e.g. 3 s @ 25 Hz = 75 samples)
4. Apply low-pass filter (α=0.3)
5. Extract 30 features (mean, std, min, max, zero-crossing rate per axis)
6. Run ML model (or rule-based fallback) → activity label
7. Add risk flags (ergo, fatigue)
8. Batch events and POST to `POST /api/events`

### 4.3 Backend (FastAPI)

1. Receive `POST /api/events`
2. Resolve or create Worker (by name/worker_id)
3. Resolve or create active Session
4. Insert events into `activity_events`
5. Update `session_aggregates` (active_pct, idle_pct, etc.)
6. Broadcast worker state to WebSocket clients

### 4.4 Dashboard (React)

1. Supervisor logs in (JWT)
2. **Live View:** WebSocket receives worker state; worker cards update in real time
3. **Alerts:** Workers with risk_ergo or risk_fatigue
4. **Shift Summary:** Sessions list and activity percentages per session

---

## 5. Data Flow Summary

| Stage | Format | Example |
|-------|--------|---------|
| Wearable → Edge | JSON over BLE | `{worker_id:"W01", ts:..., ax,ay,az,gx,gy,gz,temp}` |
| Edge → Backend | `POST /api/events` | `{worker_id, events:[{ts,label,risk_ergo,risk_fatigue}]}` |
| Backend → Dashboard | WebSocket | `{worker_id, name, current_state, risk_ergo, risk_fatigue}` |

### Activity States

- sewing, idle, adjusting, error, break

### Risk Flags

- `risk_ergo` — ergonomic risk
- `risk_fatigue` — fatigue risk

---

## 6. Current Modes (Without Hardware)

The system works end-to-end without ESP32 hardware:

| Mode | How | Use Case |
|------|-----|----------|
| **Simulator** | `python ml/simulator.py` | Generates fake events directly to backend |
| **Edge simulator** | `BLE_DEVICE_ID` empty in `edge/.env` | Edge generates fake IMU samples, runs ML, POSTs to backend |
| **Both** | Run edge + simulator with different worker IDs | Test multi-worker scenarios |

**Live View and Alerts work fully.** The only missing piece is real hardware and firmware.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `MASTER_PLAN.md` | Implementation phases and checklists |
| `RUN_ORDER.md` | Step-by-step startup |
| `TESTING_WITHOUT_HARDWARE.md` | **How to test without ESP32/wearable** |
| `PILOT_PREP.md` | Pilot deployment checklist |
| `TECHNICAL_STACK_SPEC.md` | API contracts, data formats |
| `firmware/README.md` | Firmware build and upload |
| `DEPLOYMENT_LAPTOP_ONLY.md` | Laptop-only deployment |
| `DASHBOARD_ENHANCEMENT_PLAN.md` | Plan for UI/UX, animations, charts, design |
