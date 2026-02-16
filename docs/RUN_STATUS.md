# Run Status — Industrial Wearable AI

**Checked:** 2026-02-12

## Services started

| Service      | Status   | URL / Note                    |
|-------------|----------|-------------------------------|
| PostgreSQL  | Running  | Docker container `wearable_ai_postgres` |
| Backend     | Running  | http://localhost:8000         |
| Dashboard   | Running  | http://localhost:5173         |
| Edge        | Restarted| Connects to ESP32 via BLE     |

## Verification

- **Backend health:** `GET http://localhost:8000/health` → `{"status":"ok"}`
- **Workers API:** `GET http://localhost:8000/api/workers` → returns worker list (W01, etc.)
- **Dashboard:** Open http://localhost:5173 → log in (admin / your password) → Live View, Shift Summary

## Edge ↔ ESP32 (BLE)

**Current issue:** The edge **scan** is not finding "WearableAI" (device not found in 10s scan). So either the laptop’s Bluetooth isn’t seeing the ESP32, or the ESP32 is not advertising while the scan runs.

**What was fixed in code:**

1. **Scan before connect** — Edge scans for "WearableAI" or your BLE address before connecting.
2. **Longer connect timeout** — 60 seconds (was 30).
3. **Retry on timeout** — Retries up to 5 times on timeout/not found/notify errors.

**What you can do:**

1. **ESP32:** Keep it **powered**, **close to the laptop** (within 1 m), Serial Monitor showing `[Wearable AI] BLE advertising started`.
2. **Windows:** Turn **Bluetooth** on (quick settings / Settings → Bluetooth). Unpair "WearableAI" if it appears under paired devices.
3. **Run the edge again** so it scans again (it will retry up to 5 times).

**Use simulator so the rest works:**  
To run the full stack and see the dashboard with **simulated** worker data (no ESP32 needed), in `edge/.env` set:

```env
BLE_DEVICE_ID=
```

Leave it empty. Then run the edge: `python -m src.main`. It will run in simulator mode and the dashboard at http://localhost:5173 will show worker W01 with live-updating fake data (Connected badge, Live View, Shift Summary). You can switch back to real hardware later by setting `BLE_DEVICE_ID=a4:f0:0f:8e:9c:1a` again.

## Quick links

- Dashboard: http://localhost:5173  
- API docs: http://localhost:8000/docs  
- Backend health: http://localhost:8000/health  
