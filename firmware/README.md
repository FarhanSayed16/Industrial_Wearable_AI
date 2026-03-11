# Industrial Wearable AI — ESP32 Firmware

Placeholder firmware for the wearable device. **Replace `src/main.cpp` when hardware is ready.**

## Hardware

| Component | Specification |
|-----------|---------------|
| **MCU** | ESP32-WROOM-32 (or ESP32-DevKitC) |
| **IMU** | MPU6050 (6-axis: accel + gyro), I2C 0x68 |
| **Temperature** | DHT11 or DS18B20 |
| **Power** | Li-ion 3.7V + TP4056, USB charge |

## Build & Upload

**Prerequisite:** Install [PlatformIO](https://platformio.org/) (VS Code extension or CLI: `pip install platformio`).

```bash
# From firmware/
pio run              # Build
pio run -t upload    # Flash to device
pio device monitor   # Serial monitor (115200 baud)
```

## Expected JSON Payload (Wearable → Edge)

Per `TECHNICAL_STACK_SPEC.md` §4.1:

```json
{
  "worker_id": "W01",
  "ts": 1704067200123,
  "ax": -0.3, "ay": 1.2, "az": 9.6,
  "gx": 21, "gy": -4, "gz": 3,
  "temp": 31.5
}
```

- **worker_id:** string (assigned to device)
- **ts:** Unix milliseconds
- **ax, ay, az:** acceleration (g)
- **gx, gy, gz:** gyro (°/s)
- **temp:** °C

**Transport:** BLE GATT characteristic write/notify; JSON string UTF-8.

## Final Implementation Tasks

1. Initialize I2C, MPU6050, temp sensor
2. Read IMU at 25–50 Hz
3. Read temp at 0.2–1 Hz
4. Pack JSON with ArduinoJson
5. Advertise BLE service; send via GATT
6. Store worker_id in NVS or compile-time
