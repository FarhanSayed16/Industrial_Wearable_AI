# Test Run Results — Full Stack

**Date:** 2026-02-12  
**What was run:** PostgreSQL, Backend, Edge (BLE), Dashboard.  
**Latest run:** Full stack started again; ESP32 confirmed advertising (Serial: BLE address a4:f0:0f:8e:9c:1a, BLE advertising started). Edge ran; **connection still timed out** (~65s) at `client.connect()`.

---

## Services status

| Service     | Status   | Details |
|------------|----------|---------|
| PostgreSQL | ✅ Running | Docker container `wearable_ai_postgres` |
| Backend    | ✅ Running | http://localhost:8000 — health `{"status":"ok"}` |
| Dashboard  | ✅ Running | http://localhost:5174 (port 5173 was in use) |
| Edge       | ❌ Exited | See below |

---

## Edge ↔ ESP32 — What happened

1. **Edge started** with `BLE_DEVICE_ID=a4:f0:0f:8e:9c:1a`, `WORKER_ID=W01`.
2. **Scan ran:** `Scanning for BLE device (attempt 1/5)...`
3. **Device was found** — the code got past the scan and called `client.connect()` (no "WearableAI not found" error).
4. **Connection timed out** — after ~63 seconds, `TimeoutError` in `client.connect()`. The BLE connection to the ESP32 never completed within the 60s timeout.

So: **the laptop sees the ESP32 in the BLE scan, but the connection step never completes** (Windows or ESP32 side).

---

## Conclusion

- **Backend and dashboard are fine.** You can use:
  - **Dashboard:** http://localhost:5174 (log in with admin / your password).
  - **API docs:** http://localhost:8000/docs
- **Issue:** BLE **connection** from the edge to the ESP32 times out after the device is found. Possible causes:
  - ESP32 already connected to another client (e.g. phone or other app).
  - Windows BLE stack slow or failing to complete the connection.
  - Distance or environment (try ESP32 very close to the laptop).

---

## What you can do

1. **Use the dashboard with simulated data**  
   In `edge/.env` set `BLE_DEVICE_ID=` (empty). Run the edge again: `python -m src.main`. Open http://localhost:5174 — you should see Live View with worker W01 (simulated) and "Connected".

2. **Retry real hardware**  
   - Close any other app that might be using the ESP32 (e.g. Serial Monitor is fine; close BLE scanner apps or other Python scripts).
   - Put the ESP32 very close to the laptop (e.g. 10–20 cm).
   - Unpair "WearableAI" from Windows Bluetooth settings.
   - Run the edge again and see if the connection completes before 60s.

3. **Check ESP32 serial**  
   When the edge runs, see if the ESP32 serial shows any connection or error messages when the connection is attempted.
