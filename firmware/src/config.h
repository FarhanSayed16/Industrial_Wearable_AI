#pragma once

// Hardware Pins
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#define BATTERY_ADC_PIN 34
#define STATUS_LED_PIN 2 // Built-in LED

// Sampling Rate
#define SAMPLE_RATE_HZ 25
#define SAMPLE_INTERVAL_MS (1000 / SAMPLE_RATE_HZ)

// BLE Configuration
#define BLE_DEVICE_NAME "WearableAI"
#define SERVICE_UUID "0000181A-0000-1000-8000-00805F9B34FB" // Environmental Sensing
#define SENSOR_CHAR_UUID "00002A5D-0000-1000-8000-00805F9B34FB" // Sensor Location (used for custom payload)
#define BATTERY_CHAR_UUID "00002A19-0000-1000-8000-00805F9B34FB" // Battery Level
#define INFO_CHAR_UUID "00002A24-0000-1000-8000-00805F9B34FB" // Model Number String
