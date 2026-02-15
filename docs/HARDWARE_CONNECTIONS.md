# Industrial Wearable AI — Hardware Connections & Component List

Use this doc to wire your IoT components. When everything is connected and powered, tell the team you’re ready so firmware and edge can be finalized.

---

## 1. Component List

| # | Component | Spec / Notes |
|---|-----------|--------------|
| 1 | **ESP32** | ESP32-WROOM-32 or ESP32-DevKitC (built-in BLE + WiFi) |
| 2 | **MPU6050** | 6-axis IMU (accelerometer + gyroscope), I2C address **0x68** |
| 3 | **Temperature sensor** | **Either** DHT11 **or** DS18B20 (see wiring below) |
| 4 | **Battery** | Li-ion 3.7 V, 500–1000 mAh |
| 5 | **TP4056** | Li-ion charger module (USB charge, 3.7 V out) |
| 6 | **Wires** | Jumper wires (female–female for breakout boards) |
| 7 | **Enclosure** | Optional: wrist band / case; keep temp sensor ventilated |

---

## 2. ESP32 Pin Reference (DevKitC-style)

| ESP32 pin name | GPIO# | Use in this project |
|----------------|-------|----------------------|
| SDA (I2C)      | 21    | MPU6050 SDA          |
| SCL (I2C)      | 22    | MPU6050 SCL          |
| GPIO 4         | 4     | DHT11 data **or** DS18B20 data |
| 3V3            | —     | VCC for sensors      |
| GND            | —     | GND common           |

---

## 3. Wiring Tables

### 3.1 MPU6050 → ESP32 (I2C)

| MPU6050 pin | Connect to ESP32 | Notes        |
|-------------|------------------|-------------|
| VCC         | 3V3              | 3.3 V only  |
| GND         | GND              |             |
| SDA         | GPIO 21 (SDA)    | I2C data    |
| SCL         | GPIO 22 (SCL)    | I2C clock   |
| AD0         | GND (or leave)   | GND = I2C addr 0x68 |

Some boards label **SDA/SCL** as **SDA/SCL**; others as **SDI/SCK**. Use the I2C data/clock pins.

### 3.2 DHT11 → ESP32 (if using DHT11)

| DHT11 pin | Connect to ESP32 | Notes          |
|-----------|------------------|----------------|
| VCC       | 3V3              | 3.3 V          |
| GND       | GND              |                |
| DATA      | GPIO 4            | Single data pin |
| (NC)      | —                | No pull-up needed on most modules |

### 3.3 DS18B20 → ESP32 (if using DS18B20)

| DS18B20 pin | Connect to ESP32 | Notes |
|-------------|------------------|--------|
| VCC (red)   | 3V3              |       |
| GND (black) | GND              |       |
| DATA (yellow) | GPIO 4          | **4.7 kΩ pull-up** from DATA to 3V3 |

Use one 4.7 kΩ resistor between DATA and 3V3.

### 3.4 Power (Battery + TP4056)

| From | To | Notes |
|------|-----|--------|
| TP4056 **B+** | Battery **+** | Red |
| TP4056 **B-** | Battery **-** | Black |
| TP4056 **OUT+** | ESP32 **VIN** (or 5V if board has regulator) | 3.7 V in |
| TP4056 **OUT-** | ESP32 **GND** | Common GND |
| USB | TP4056 micro-USB | Charging only |

**Important:** Use a common GND: ESP32 GND, MPU6050 GND, sensor GND, and TP4056 OUT- should all be tied together.

---

## 4. Connection Summary (One Diagram)

```
                    ESP32 (DevKitC)
                 ┌──────────────────┐
     MPU6050     │                  │
     VCC ────────┤ 3V3              │
     GND ────────┤ GND              │
     SDA ────────┤ GPIO 21 (SDA)    │
     SCL ────────┤ GPIO 22 (SCL)    │
                 │                  │
     DHT11       │                  │    TP4056
     VCC ────────┤ 3V3              │    OUT+ ──── VIN (ESP32)
     GND ────────┤ GND              │    OUT- ──── GND (ESP32)
     DATA ───────┤ GPIO 4           │
                 │                  │
                 └──────────────────┘

     If DS18B20: DATA → GPIO 4, and 4.7kΩ from DATA to 3V3
```

---

## 5. BLE (For When Firmware Is Flashed)

The edge gateway expects BLE GATT **notify** on this characteristic UUID (must match firmware):

| Item | Value |
|------|--------|
| **GATT characteristic UUID** | `0000fff1-0000-1000-8000-00805f9b34fb` |

After you flash firmware, you’ll get the ESP32’s **BLE MAC address**. That goes in `edge/.env` as `BLE_DEVICE_ID`.

---

## 6. Checklist Before Saying “Ready”

Use this to confirm everything is in place:

- [ ] ESP32 powered (USB or battery via TP4056)
- [ ] MPU6050 wired: VCC→3V3, GND→GND, SDA→21, SCL→22
- [ ] Temperature sensor wired: **either** DHT11 (DATA→GPIO4) **or** DS18B20 (DATA→GPIO4 + 4.7kΩ to 3V3)
- [ ] All GNDs connected together (ESP32, MPU6050, sensor, TP4056 OUT-)
- [ ] No shorts (VCC not touching GND)
- [ ] (Optional) Serial monitor at 115200 baud to see debug output after firmware is flashed

When this is done, you can say **“Hardware is connected and ready”** and we’ll proceed with firmware and edge configuration (worker_id, BLE_DEVICE_ID, GATT UUID).

---

## 7. Quick Reference

| Sensor | Interface | ESP32 pins |
|--------|-----------|------------|
| MPU6050 | I2C (0x68) | SDA=21, SCL=22, VCC=3V3, GND=GND |
| DHT11   | 1-wire     | DATA=4, VCC=3V3, GND=GND |
| DS18B20 | 1-wire     | DATA=4 (+ 4.7kΩ to 3V3), VCC=3V3, GND=GND |

**Document version:** 1.0  
**Related:** `firmware/README.md`, `PROJECT_STATUS_AND_ARCHITECTURE.md`, `edge/.env.example`

---

## WHO_AM_I = 0x70 ("chip not MPU6050")

If your serial shows **WHO_AM_I = 0x70** and a message like "chip not MPU6050" or "MPU6050 not found", the board is likely an **MPU9250** (or MPU6500 / clone), not an MPU6050. Many breakouts sold as "MPU6050" or "GY-91" use the MPU9250; it uses the same accel/gyro register map, so it works with MPU6050 code.

**Fix:** The Adafruit MPU6050 library in this project has been patched to accept WHO_AM_I **0x70** as well as 0x68. Rebuild and upload the firmware (Arduino IDE or PlatformIO). If you reinstall or update the library (e.g. via Library Manager), you may need to re-apply the change in `Adafruit_MPU6050.cpp`: change the chip-id check to accept both `0x68` and `0x70`.

---

## Troubleshooting: "MPU6050 not found"

If the ESP32 serial shows **`[Wearable AI] MPU6050 not found`**:

1. **Startup timing** — The firmware now waits 150 ms after I2C init and retries MPU init up to 3 times. If it still fails, increase `MPU_INIT_DELAY_MS` (e.g. 300 or 500) or `MPU_INIT_RETRIES` in `IndustrialWearableAI.ino`. If your unit test works with the same wiring, the main sketch may be talking to I2C too soon; the delay and retries should fix that.
2. **I2C address** — Most MPU6050 modules use address **0x68** (AD0 pin to GND). If your module has AD0 tied to VCC, the address is **0x69**. In `IndustrialWearableAI.ino` set `#define MPU_I2C_ADDR 0x69` to match your unit test.
3. **SDA/SCL pins** — The example uses **GPIO 21 (SDA)** and **GPIO 22 (SCL)**. Some ESP32 boards use different I2C pins (e.g. 4 and 15). Check your board’s pinout and set `SDA_PIN` / `SCL_PIN` in the firmware to match.
4. **Wiring** — Confirm VCC→3V3, GND→GND, SDA→SDA, SCL→SCL. Swap SDA/SCL only if your board labels them the other way.
5. **Dashboard without MPU** — When the MPU is not found, the firmware only sends device status (no fake IMU data). The dashboard can still show the worker with a “No MPU connected” message. Fix the MPU wiring to get real motion data.

---

## Troubleshooting: Worker shows “Idle” instead of “Working”

If the MPU is connected and the ESP32 is sending data, but the dashboard always shows **Idle** (or rarely “Working” / “Sewing”):

1. **Activity comes from the edge classifier** — The edge gateway buffers IMU samples, extracts features, and runs a rule-based classifier (or ML model). The label (idle / adjusting / sewing) is sent to the backend and shown on the dashboard.
2. **Rule-based thresholds** — With no ML model, the edge uses variance of accel/gyro in a short window. The thresholds in `edge/src/classifier.py` are tuned so that normal hand/arm motion (sewing) should show as **sewing** or **adjusting**. If your motion is very subtle or the sensor is very smooth, it may still classify as idle.
3. **What to do** — Move the wearable (e.g. hand/wrist) with clear, repeated motion while the edge is running; the state should switch to “Working” or “Sewing” as events are posted. If it still stays Idle, you can lower the idle thresholds further in `_rule_based_predict()` (e.g. `var_sum < 0.06` → `0.03`, `var_max < 0.12` → `0.06`) so that even small motion is treated as non-idle.
4. **Using an ML model** — For better accuracy, train and use a model (see `ml/`) and set `MODEL_PATH` in `edge/.env` so the edge loads it instead of the rule-based fallback.

---

## After Wiring: See Real-Time Data on the Dashboard

Once everything is connected, follow **`docs/REALTIME_DATA_SETUP.md`** to:

1. Flash the firmware to the ESP32  
2. Find the ESP32 BLE address  
3. Set `edge/.env` (`BLE_DEVICE_ID`, `WORKER_ID`)  
4. Run backend, edge, and dashboard  
5. Open the website and see live worker data (Live View, “Connected” badge)
