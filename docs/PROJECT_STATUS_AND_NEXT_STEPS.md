# Industrial Wearable AI — Project Status & Next Steps

**Document:** Clear overview of what’s done, what’s left, login, ESP workflow, and how to proceed.  
**Version:** 1.0  
**Last updated:** 2025-02-09

---

## Table of Contents

1. [What’s Left in the Project](#1-whats-left-in-the-project)
2. [Is the App Work Done?](#2-is-the-app-work-done)
3. [How Do Users Login?](#3-how-do-users-login)
4. [How Does the ESP Work?](#4-how-does-the-esp-work)
5. [How Can It Detect Many Workers and Store Data?](#5-how-can-it-detect-many-workers-and-store-data)
6. [What Must Be Configured After Hardware Is Connected?](#6-what-must-be-configured-after-hardware-is-connected)
7. [Next Steps (Recommended Order)](#7-next-steps-recommended-order)

---

## 1. What’s Left in the Project

| Area | Status | Notes |
|------|--------|-------|
| **Dashboard** | ✅ Done | Phases 0–5 complete. Phase 6 (accessibility) is optional polish. |
| **Backend** | ✅ Done | API, auth, WebSocket, PostgreSQL |
| **Edge** | ✅ Done | BLE client, ML pipeline, API client, simulator mode |
| **ML** | ✅ Done | Training, model export, simulator |
| **Firmware** | ⚠️ Placeholder only | `main.cpp` is a stub; needs full ESP32 implementation when hardware is ready |

---

## 2. Is the App Work Done?

**Yes.** The dashboard is feature-complete:

- **Login** — JWT auth, remember me, polished UI
- **Live View** — Worker cards, real-time updates, KPIs, filters, search, sort
- **Alerts Panel** — Severity indicators, expand/collapse
- **Shift Summary** — Sessions list, activity donut, date filter, auto-refresh
- **UX** — Keyboard shortcuts (`?` for help, `Esc` to close), logout confirmation

---

## 3. How Do Users Login?

| Item | Details |
|------|---------|
| **Method** | JWT-based HTTP auth |
| **Default** | `admin` / `admin123` |
| **Change password** | `python backend/change_password.py admin` (required before pilot) |
| **URL** | `http://localhost:5173/login` |
| **Users** | Only admin user exists; no registration UI |

---

## 4. How Does the ESP Work?

**Flow:**

1. **ESP32** reads MPU6050 (IMU) at ~25 Hz and temp sensor at ~0.2–1 Hz
2. Sends JSON over BLE GATT: `{worker_id, ts, ax, ay, az, gx, gy, gz, temp}`
3. **Edge** connects to wearable via BLE, reads stream
4. Edge buffers samples, runs ML, POSTs events to backend
5. **Backend** stores events, updates sessions, broadcasts to dashboard via WebSocket

**Firmware:** `firmware/src/main.cpp` is a placeholder. Replace with full implementation when hardware is ready (see `firmware/README.md`).

---

## 5. How Can It Detect Many Workers and Store Data?

| Setup | How |
|------|-----|
| **Multiple wearables** | Run **one edge process per wearable** — each with its own `WORKER_ID` and `BLE_DEVICE_ID` |
| **Simulator** | `python ml/simulator.py --worker W01` (run multiple with W02, W03, … in separate terminals) |
| **Edge + simulator** | Run edge (e.g. W01) and simulator (W02, W03) together for mixed testing |

All workers share the same backend and dashboard. The dashboard shows all workers in Live View and Shift Summary.

**Data storage:** PostgreSQL stores workers, sessions, activity events, and session aggregates. Backend handles upserts and aggregates.

---

## 6. What Must Be Configured After Hardware Is Connected?

| What | Where / How |
|------|-------------|
| **Worker ID** | Firmware (NVS or compile-time) and `edge/.env` → `WORKER_ID` |
| **BLE device** | `edge/.env` → `BLE_DEVICE_ID` (MAC address of wearable) |
| **GATT UUID** | Must match between firmware and `edge/src/ble_client.py` |
| **Admin password** | `python backend/change_password.py admin` before pilot |
| **Production env** | `backend/.env`, `edge/.env`, `dashboard/.env` (see `PILOT_PREP.md`) |

### Configuration checklist (per wearable)

1. Flash firmware with correct `worker_id`
2. Set `WORKER_ID` and `BLE_DEVICE_ID` in `edge/.env` for that edge instance
3. Ensure GATT characteristic UUID in firmware matches `edge/src/ble_client.py`

---

## 7. Next Steps (Recommended Order)

### Without hardware (right now)

1. **Test end-to-end with simulator**
   - Follow `docs/RUN_ORDER.md` (Postgres, backend, dashboard)
   - Run `python ml/simulator.py --worker W01 --duration 60 --interval 2`
   - Open `http://localhost:5173` → login → Live View and Shift Summary

2. **Change admin password**
   ```powershell
   cd backend
   python change_password.py admin
   ```

3. **Test multi-worker**
   - Run multiple simulator instances with different `--worker` IDs
   - Verify Live View shows all workers

### With hardware

1. **Assemble** — ESP32, MPU6050, temp sensor, battery, enclosure  
2. **Implement firmware** — IMU + temp + BLE (see `firmware/README.md`, `PROJECT_STATUS_AND_ARCHITECTURE.md`)  
3. **Flash** — Via PlatformIO  
4. **Configure edge** — `WORKER_ID`, `BLE_DEVICE_ID`, GATT UUID match  
5. **Run** — One edge process per wearable  

### Optional polish

- Phase 6: accessibility (focus, ARIA, contrast, favicon)
- User registration / multi-user management (if needed)

---

## Summary

| Question | Answer |
|----------|--------|
| App done? | Yes |
| Login? | JWT via `admin` / `admin123` (change before pilot) |
| ESP role? | Read IMU/temp, send JSON over BLE to edge |
| Multi-worker? | One edge per wearable; all visible in dashboard |
| Hardware left? | Yes — firmware implementation and wiring |
| Config after hardware? | Firmware worker ID, `edge/.env` (WORKER_ID, BLE_DEVICE_ID), GATT UUID match |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `PROJECT_STATUS_AND_ARCHITECTURE.md` | Architecture, data flow, IoT config |
| `RUN_ORDER.md` | Startup order |
| `PILOT_PREP.md` | Pilot deployment checklist |
| `TESTING_WITHOUT_HARDWARE.md` | Testing without ESP32 |
| `firmware/README.md` | Firmware build and upload |
