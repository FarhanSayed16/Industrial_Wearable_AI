#pragma once
#include <Arduino.h>

struct SensorData {
    float ax, ay, az;
    float gx, gy, gz;
    float temp;
};

void initSensors();
bool readSensors(SensorData& data);
bool isMpuConnected();
