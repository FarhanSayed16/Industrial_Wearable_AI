#include <Arduino.h>
#include <NimBLEDevice.h>
#include <ArduinoJson.h>
#include "config.h"
#include "sensors.h"
#include "battery.h"

NimBLEServer* pServer = nullptr;
NimBLECharacteristic* pSensorChar = nullptr;
NimBLECharacteristic* pBatteryChar = nullptr;
NimBLECharacteristic* pInfoChar = nullptr;

bool deviceConnected = false;
unsigned long lastSampleTime = 0;
unsigned long lastBatteryTime = 0;

class MyServerCallbacks : public NimBLEServerCallbacks {
    void onConnect(NimBLEServer* pServer) {
        deviceConnected = true;
        Serial.println("Client connected");
        digitalWrite(STATUS_LED_PIN, HIGH);
    }
    void onDisconnect(NimBLEServer* pServer) {
        deviceConnected = false;
        Serial.println("Client disconnected");
        digitalWrite(STATUS_LED_PIN, LOW);
        NimBLEDevice::startAdvertising(); // Restart advertising to allow reconnection
    }
};

void setupBLE() {
    NimBLEDevice::init(BLE_DEVICE_NAME);
    NimBLEDevice::setPower(ESP_PWR_LVL_P9); // Max transmission power (+9dbm)
    
    pServer = NimBLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());
    
    NimBLEService* pService = pServer->createService(SERVICE_UUID);
    
    // Core Sensor Data Stream Characteristic
    pSensorChar = pService->createCharacteristic(
        SENSOR_CHAR_UUID,
        NIMBLE_PROPERTY::NOTIFY
    );
    
    // Battery Reporting Characteristic
    pBatteryChar = pService->createCharacteristic(
        BATTERY_CHAR_UUID,
        NIMBLE_PROPERTY::NOTIFY | NIMBLE_PROPERTY::READ
    );
    
    // General Device Info Characteristic
    pInfoChar = pService->createCharacteristic(
        INFO_CHAR_UUID,
        NIMBLE_PROPERTY::READ
    );
    
    pService->start();
    
    NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->start();
    
    Serial.println("BLE Advertising Started");
}

void setup() {
    Serial.begin(115200);
    
    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);
    
    initSensors();
    initBattery();
    setupBLE();

    // Populate static data
    JsonDocument infoDoc;
    infoDoc["fw_version"] = "1.0.0";
    infoDoc["mpu_connected"] = isMpuConnected();
    String infoStr;
    serializeJson(infoDoc, infoStr);
    pInfoChar->setValue(infoStr);
}

void loop() {
    unsigned long now = millis();
    
    // Stream 6-axis IMU JSON payloads via BLE at 25Hz
    if (deviceConnected && (now - lastSampleTime >= SAMPLE_INTERVAL_MS)) {
        lastSampleTime = now;
        
        SensorData sdata;
        if (readSensors(sdata)) {
            JsonDocument doc;
            doc["ts"] = now;
            doc["ax"] = sdata.ax;
            doc["ay"] = sdata.ay;
            doc["az"] = sdata.az;
            doc["gx"] = sdata.gx;
            doc["gy"] = sdata.gy;
            doc["gz"] = sdata.gz;
            doc["temp"] = sdata.temp;
            
            String jsonStr;
            serializeJson(doc, jsonStr);
            
            pSensorChar->setValue(jsonStr);
            pSensorChar->notify();
            
        } else {
             // Fallback if sensor fails mid-operation
             JsonDocument doc;
             doc["mpu_connected"] = false;
             String jsonStr;
             serializeJson(doc, jsonStr);
             pSensorChar->setValue(jsonStr);
             pSensorChar->notify();
        }
    }
    
    // Periodically notify Battery status every 60 seconds
    if (deviceConnected && (now - lastBatteryTime >= 60000)) {
        lastBatteryTime = now;
        int pct = getBatteryPercentage();
        JsonDocument bDoc;
        bDoc["battery_pct"] = pct;
        String bStr;
        serializeJson(bDoc, bStr);
        pBatteryChar->setValue(bStr);
        pBatteryChar->notify();
    }
}
