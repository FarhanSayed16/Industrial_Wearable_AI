#include "sensors.h"
#include "config.h"
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;
bool mpu_connected = false;

void initSensors() {
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    Serial.println("Initializing MPU6050...");
    
    if (!mpu.begin()) {
        Serial.println("Failed to find MPU6050 chip");
        mpu_connected = false;
        return;
    }
    
    mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
    mpu.setGyroRange(MPU6050_RANGE_250_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    
    mpu_connected = true;
    Serial.println("MPU6050 Found!");
}

bool readSensors(SensorData& data) {
    if (!mpu_connected) return false;
    
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    
    data.ax = a.acceleration.x;
    data.ay = a.acceleration.y;
    data.az = a.acceleration.z;
    
    data.gx = g.gyro.x;
    data.gy = g.gyro.y;
    data.gz = g.gyro.z;
    
    data.temp = temp.temperature;
    return true;
}

bool isMpuConnected() {
    return mpu_connected;
}
