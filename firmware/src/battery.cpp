#include "battery.h"
#include "config.h"
#include <Arduino.h>

void initBattery() {
    pinMode(BATTERY_ADC_PIN, INPUT);
}

int getBatteryPercentage() {
    // Basic voltage divider reading
    // Assuming 3.3V reference and 12-bit ADC (0-4095)
    // Adjust according to the actual voltage divider circuit
    int rawValue = analogRead(BATTERY_ADC_PIN);
    
    // Simplistic mapping for LiPo 3.2V - 4.2V using a voltage divider (e.g. 1:1)
    float voltage = (rawValue / 4095.0) * 3.3 * 2; 
    
    int pct = (voltage - 3.2) / (4.2 - 3.2) * 100;
    if (pct > 100) pct = 100;
    if (pct < 0) pct = 0;
    
    return pct;
}
