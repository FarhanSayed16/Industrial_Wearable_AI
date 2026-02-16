# See Real-Time Data on the Dashboard (Hardware Connected)

After you’ve wired the ESP32 + MPU6050 + DHT11 (see `HARDWARE_CONNECTIONS.md`), follow these steps so the **admin sees live worker data** on the website.

---

## How the admin sees details

1. **Backend** receives events from the edge and updates worker state.
2. **Dashboard** connects to the backend over **WebSocket**.
3. **Live View** shows worker cards that update in **real time** (state, risks, “Updated X ago”).
4. **Header** shows **“Connected”** when the WebSocket is up; **“Disconnected”** when it’s not.
5. **Shift Summary** shows sessions and activity percentages.

So: **ESP32 → BLE → Edge → Backend → WebSocket → Dashboard**. All details the admin sees come from this chain.

---

## Step 1: Flash the firmware to the ESP32

From the project root:

```powershell
cd D:\Industrial_Wearable_AI\firmware
pio run -t upload
```

- Connect the ESP32 by USB and choose the correct COM port if asked.
- After flashing, open the serial monitor to confirm it’s running:

```powershell
pio device monitor -b 115200
```

You should see lines like:

- `[Wearable AI] MPU6050 OK`
- `[Wearable AI] DHT11 OK` (or “using placeholder temp” if DHT isn’t used)
- `[Wearable AI] BLE advertising as "WearableAI"`

Leave the ESP32 powered (USB or battery). It will advertise over BLE.

---

## Step 2: Find the ESP32 BLE address

The edge gateway needs the **BLE MAC address** of the wearable.

**Option A – Serial monitor (easiest)**  
Add a one-time print of the BLE address in firmware (see “Optional: Print BLE address” below), then read it from the serial monitor after boot.

**Option B – Scanner app**  
Use a BLE scanner app on your phone (e.g. “nRF Connect”, “BLE Scanner”). Look for a device named **“WearableAI”**. The address is shown as something like `AA:BB:CC:DD:EE:FF` or `AABBCCDDEEFF`.

**Option C – From the laptop (Python)**  
Run a short script that scans and lists BLE devices; pick the one named “WearableAI” and use its address.

Example (with `bleak` installed):

```powershell
cd D:\Industrial_Wearable_AI\edge
.venv\Scripts\Activate.ps1
python -c "
import asyncio
from bleak import BleakScanner
async def scan():
    devs = await BleakScanner.discover(timeout=5.0)
    for d in devs:
        if d.name and 'Wearable' in d.name:
            print('Name:', d.name, 'Address:', d.address)
asyncio.run(scan())
"
```

Use the **Address** value (e.g. `XX:XX:XX:XX:XX:XX`) as `BLE_DEVICE_ID` in the next step.

---

## Step 3: Configure the edge gateway

Edit `edge/.env` (or create it from `edge/.env.example`):

```env
BACKEND_URL=http://localhost:8000
WORKER_ID=W01
BLE_DEVICE_ID=XX:XX:XX:XX:XX:XX
```

- Replace `XX:XX:XX:XX:XX:XX` with the **actual BLE address** from Step 2.
- `WORKER_ID` must match what you use in firmware (default in firmware is `W01`). This is the “worker” that will appear on the dashboard.

If `BLE_DEVICE_ID` is empty, the edge runs in **simulator mode** (fake data) and does not connect to your hardware.

---

## Step 4: Run the full stack (backend, edge, dashboard)

Use **four terminals** (same as in `RUN_ORDER.md`).

**Terminal 1 – PostgreSQL**

```powershell
cd D:\Industrial_Wearable_AI\backend
docker compose up -d
```

**Terminal 2 – Backend**

```powershell
cd D:\Industrial_Wearable_AI\backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 3 – Edge (connects to ESP32 over BLE)**

```powershell
cd D:\Industrial_Wearable_AI\edge
.venv\Scripts\Activate.ps1
python -m src.main
```

You should see logs like: `Edge starting: worker=W01, backend=..., simulator=False` and then BLE connection activity. If the edge connects to the ESP32, it will start posting events to the backend.

**Terminal 4 – Dashboard**

```powershell
cd D:\Industrial_Wearable_AI\dashboard
npm run dev
```

---

## Step 5: Open the dashboard and log in

1. Open **http://localhost:5173** in your browser.
2. Log in (e.g. `admin` / your password).
3. On **Live View**:
   - The header should show **“Connected”** (green) when the WebSocket is connected to the backend.
   - You should see a **worker card** for `W01` (or whatever `WORKER_ID` you set), with state (e.g. sewing, idle) and “Updated …” updating in real time.
4. **Shift Summary** will show sessions and activity for that worker once there is enough data.

If the header shows **“Disconnected”**, the browser is not connected to the backend WebSocket. Check that the backend is running and that you’re using the correct URL (and that nothing is blocking WebSocket).

---

## Why it might not look “connected”

| What you see | What to check |
|--------------|----------------|
| **“Disconnected”** in header | Backend running? Dashboard URL correct (e.g. `http://localhost:5173`)? Try refreshing the page. |
| No worker cards | Edge running? `BLE_DEVICE_ID` set in `edge/.env`? ESP32 powered and advertising? Edge logs show connection to the device? |
| Edge doesn’t connect to ESP32 | BLE address correct in `edge/.env`? ESP32 firmware flashed and serial shows “BLE advertising”? Laptop BLE on and close to the device? |
| **“Could not start notify … Unreachable”** (Windows) | Windows often blocks notify when the wearable is **paired**. **Fix:** Open **Settings > Bluetooth & devices**, find **WearableAI**, click **Remove device** (unpair). Then run the edge again. Do not re-pair; Bleak connects without pairing. |
| Worker card stuck or old data | Edge may have lost BLE link; restart the edge process and ensure ESP32 is still powered and advertising. |

---

## Optional: Print BLE address in firmware

To get the address from the serial monitor, you can print it once at startup.

In `firmware/src/main.cpp`, after `NimBLEDevice::init(BLE_DEVICE_NAME);` add:

```cpp
Serial.print("[Wearable AI] BLE address: ");
Serial.println(NimBLEDevice::getAddress().toString().c_str());
```

Then run `pio device monitor -b 115200`, reset the ESP32, and copy the printed address into `edge/.env` as `BLE_DEVICE_ID`.

---

## Summary

1. Flash firmware → ESP32 advertises as **“WearableAI”** and sends IMU + temp over BLE.
2. Find ESP32 BLE address (serial, scanner app, or Python script).
3. Set `edge/.env`: `BLE_DEVICE_ID=<address>`, `WORKER_ID=W01`.
4. Run Postgres, backend, edge, dashboard (same commands as in `RUN_ORDER.md`).
5. Open the dashboard and log in; **Live View** and **Shift Summary** show real-time details for the admin.

The **connection** the admin cares about is the **WebSocket (dashboard ↔ backend)**. The **data** comes from **ESP32 → Edge → Backend**. Once the edge is connected to the ESP32 and the backend is running, the dashboard will show live data.
