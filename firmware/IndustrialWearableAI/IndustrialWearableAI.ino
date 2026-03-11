/*
 * Industrial Wearable AI — ESP32 Firmware (Arduino IDE)
 * Reads MPU6050 (IMU); sends JSON over BLE GATT notify.
 * Libraries: Install via Sketch > Include Library > Manage Libraries:
 *   - Adafruit MPU6050
 *   - Adafruit Unified Sensor
 *   - ArduinoJson
 *   - NimBLE-Arduino (by h2zero)
 * Board: ESP32 Dev Module (Tools > Board > ESP32 Arduino > ESP32 Dev Module)
 */
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <ArduinoJson.h>
#include <NimBLEDevice.h>

// ----- Config -----
#define WORKER_ID       "W01"
#define SDA_PIN         21
#define SCL_PIN         22
#define IMU_RATE_HZ     25
// MPU6050 I2C address: 0x68 (AD0 to GND) or 0x69 (AD0 to VCC). Try 0x69 if 0x68 fails.
#define MPU_I2C_ADDR    0x68
#define MPU_INIT_DELAY_MS  150   // Wait after Wire.begin() so MPU is ready
#define MPU_INIT_RETRIES  3     // Retry begin() this many times
#define BLE_DEVICE_NAME "WearableAI"
#define BLE_SERVICE_UUID        "0000fff0-0000-1000-8000-00805f9b34fb"
#define BLE_CHARACTERISTIC_UUID "0000fff1-0000-1000-8000-00805f9b34fb"

Adafruit_MPU6050 mpu;
NimBLEServer* pServer = NULL;
NimBLECharacteristic* pNotifyChar = NULL;
unsigned long lastImuTime = 0;
unsigned long lastStatusTime = 0;
float lastTemp = 25.0f;
const unsigned long imuIntervalMs = 1000UL / IMU_RATE_HZ;
const unsigned long statusIntervalMs = 2000UL;  // When no MPU, send status every 2 s
bool imuOk = false;

void sendStatus(bool mpuConnected) {
  StaticJsonDocument<128> doc;
  doc["worker_id"] = WORKER_ID;
  doc["mpu_connected"] = mpuConnected;
  doc["ts"] = millis();
  char buf[128];
  size_t len = serializeJson(doc, buf);
  if (len > 0 && pNotifyChar != NULL && pServer->getConnectedCount() > 0) {
    pNotifyChar->setValue((uint8_t*)buf, len);
    pNotifyChar->notify();
  }
}

void sendSample(float ax, float ay, float az, float gx, float gy, float gz, float temp) {
  StaticJsonDocument<256> doc;
  doc["worker_id"] = WORKER_ID;
  doc["ts"] = millis();
  doc["ax"] = round(ax * 100.0f) / 100.0f;
  doc["ay"] = round(ay * 100.0f) / 100.0f;
  doc["az"] = round(az * 100.0f) / 100.0f;
  doc["gx"] = round(gx * 10.0f) / 10.0f;
  doc["gy"] = round(gy * 10.0f) / 10.0f;
  doc["gz"] = round(gz * 10.0f) / 10.0f;
  doc["temp"] = round(temp * 10.0f) / 10.0f;

  char buf[256];
  size_t len = serializeJson(doc, buf);
  if (len > 0 && pNotifyChar != NULL && pServer->getConnectedCount() > 0) {
    pNotifyChar->setValue((uint8_t*)buf, len);
    pNotifyChar->notify();
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("[Wearable AI] Booting...");

  Wire.begin(SDA_PIN, SCL_PIN);
  delay(MPU_INIT_DELAY_MS);  // Give MPU6050 time to be ready after power-up / I2C init

  for (int attempt = 0; attempt < MPU_INIT_RETRIES && !imuOk; attempt++) {
    if (attempt > 0) {
      delay(100);
      Serial.println("[Wearable AI] Retrying MPU6050 init...");
    }
    if (mpu.begin(MPU_I2C_ADDR)) {
      mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
      mpu.setGyroRange(MPU6050_RANGE_250_DEG);
      mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
      imuOk = true;
      Serial.println("[Wearable AI] MPU6050 OK");
      break;
    }
  }
  if (!imuOk) {
    Serial.println("[Wearable AI] MPU6050 not found (check wiring, I2C address 0x68/0x69, and try MPU_I2C_ADDR in code)");
  }

  Serial.println("[Wearable AI] Temp: placeholder 25 C");

  NimBLEDevice::init(BLE_DEVICE_NAME);
  Serial.print("[Wearable AI] BLE address: ");
  Serial.println(NimBLEDevice::getAddress().toString().c_str());
  pServer = NimBLEDevice::createServer();

  NimBLEService* pService = pServer->createService(BLE_SERVICE_UUID);
  pNotifyChar = pService->createCharacteristic(
      BLE_CHARACTERISTIC_UUID,
      NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY);
  pNotifyChar->setValue("{}");
  pService->start();

  NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(BLE_SERVICE_UUID);
  pAdvertising->start();

  Serial.println("[Wearable AI] BLE advertising started");
}

void loop() {
  unsigned long now = millis();

  if (imuOk) {
    if (now - lastImuTime >= imuIntervalMs) {
      lastImuTime = now;
      float ax = 0, ay = 0, az = 0, gx = 0, gy = 0, gz = 0;
      sensors_event_t a, g, t;
      if (mpu.getEvent(&a, &g, &t)) {
        ax = a.acceleration.x;
        ay = a.acceleration.y;
        az = a.acceleration.z;
        gx = g.gyro.x * 57.2958f;
        gy = g.gyro.y * 57.2958f;
        gz = g.gyro.z * 57.2958f;
      }
      sendSample(ax, ay, az, gx, gy, gz, lastTemp);
    }
  } else {
    // No MPU: do not send fake data; only send status so dashboard can show "No MPU connected"
    if (now - lastStatusTime >= statusIntervalMs) {
      lastStatusTime = now;
      sendStatus(false);
    }
  }

  delay(1);
}
