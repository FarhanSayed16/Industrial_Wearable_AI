Industrial Wearable AI — Arduino IDE sketch
============================================

1. Open in Arduino IDE: File > Open > IndustrialWearableAI folder > IndustrialWearableAI.ino

2. Install ESP32 board support (if not already):
   File > Preferences > Additional Boards Manager URLs:
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   Then: Tools > Board > Boards Manager > search "esp32" > Install "esp32 by Espressif"

3. Install libraries (Sketch > Include Library > Manage Libraries):
   - Search "Adafruit MPU6050" → Install
   - Search "Adafruit Unified Sensor" → Install (if not installed by MPU6050)
   - Search "ArduinoJson" → Install (by Benoit Blanchon, v6.x)
   - Search "NimBLE" → Install "NimBLE-Arduino" by h2zero

4. Select board: Tools > Board > ESP32 Arduino > ESP32 Dev Module

5. Select correct COM port: Tools > Port

6. Upload: Sketch > Upload

7. Open Serial Monitor: Tools > Serial Monitor, set baud rate to 115200
   You should see BLE address and "BLE advertising started". Use that address in edge/.env as BLE_DEVICE_ID.
