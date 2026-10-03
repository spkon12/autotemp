#include <Arduino.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#include "secrets.h"

static const gpio_num_t DS18B20_GPIO = GPIO_NUM_4;
static const uint32_t WIFI_RETRY_MS = 5000;

OneWire oneWire(DS18B20_GPIO);
DallasTemperature sensors(&oneWire);

static bool wifi_connected = false;

static String formatAddress(const DeviceAddress &addr)
{
    char buf[17];
    snprintf(buf, sizeof(buf), "%02X%02X%02X%02X%02X%02X%02X%02X",
             addr[0], addr[1], addr[2], addr[3], addr[4], addr[5], addr[6], addr[7]);
    return String(buf);
}

static void logDiscoveredSensors()
{
    const uint8_t count = sensors.getDeviceCount();
    Serial.printf("DS18B20 devices found: %u\n", count);

    DeviceAddress addr;
    for (uint8_t i = 0; i < count; i++) {
        if (sensors.getAddress(addr, i)) {
            Serial.printf("  [%u] %s\n", i, formatAddress(addr).c_str());
        } else {
            Serial.printf("  [%u] address read failed\n", i);
        }
    }
}

static void onWiFiEvent(WiFiEvent_t event)
{
    switch (event) {
    case ARDUINO_EVENT_WIFI_STA_START:
        Serial.println("WiFi STA starting");
        break;
    case ARDUINO_EVENT_WIFI_STA_CONNECTED:
        Serial.println("WiFi connected to AP");
        break;
    case ARDUINO_EVENT_WIFI_STA_GOT_IP:
        wifi_connected = true;
        Serial.print("WiFi ready, IP: ");
        Serial.println(WiFi.localIP());
        break;
    case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
        wifi_connected = false;
        Serial.println("WiFi disconnected, will retry");
        break;
    default:
        break;
    }
}

static bool ensureWiFi()
{
    if (WiFi.status() == WL_CONNECTED) {
        return true;
    }

    Serial.printf("Connecting to WiFi SSID '%s'...\n", WIFI_SSID);
    WiFi.disconnect(true);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    const uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - start) < 15000) {
        delay(250);
    }

    if (WiFi.status() == WL_CONNECTED) {
        wifi_connected = true;
        Serial.print("WiFi connected, IP: ");
        Serial.println(WiFi.localIP());
        return true;
    }

    Serial.println("WiFi connection failed");
    wifi_connected = false;
    return false;
}

static bool postReadings(const String &payload)
{
    HTTPClient http;
    http.setTimeout(5000);
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    const int code = http.POST(payload);
    if (code <= 0) {
        Serial.printf("HTTP POST failed: %s\n", http.errorToString(code).c_str());
        http.end();
        return false;
    }

    Serial.printf("Server response HTTP %d\n", code);
    if (code >= 400) {
        Serial.println(http.getString());
    }
    http.end();
    return code >= 200 && code < 300;
}

static String buildPayload(const String readingsJson)
{
    String payload = "{\"node_id\":\"";
    payload += NODE_ID;
    payload += "\",\"readings\":[";
    payload += readingsJson;
    payload += "]}";
    return payload;
}

void setup()
{
    Serial.begin(115200);
    delay(500);
    Serial.printf("autotemp node %s starting\n", NODE_ID);

    WiFi.onEvent(onWiFiEvent);
    sensors.begin();
    logDiscoveredSensors();
    ensureWiFi();
}

void loop()
{
    static uint32_t last_wifi_attempt = 0;

    if (!wifi_connected || WiFi.status() != WL_CONNECTED) {
        const uint32_t now = millis();
        if (now - last_wifi_attempt >= WIFI_RETRY_MS) {
            last_wifi_attempt = now;
            ensureWiFi();
        }
    }

    sensors.requestTemperatures();

    const uint8_t count = sensors.getDeviceCount();
    if (count == 0) {
        Serial.println("No DS18B20 sensors detected on bus");
        delay(READ_INTERVAL_MS);
        return;
    }

    String readingsJson;
    uint8_t valid = 0;
    DeviceAddress addr;

    for (uint8_t i = 0; i < count; i++) {
        if (!sensors.getAddress(addr, i)) {
            Serial.printf("Sensor index %u: address unavailable\n", i);
            continue;
        }

        const String sensorId = formatAddress(addr);
        const float tempC = sensors.getTempC(addr);

        if (tempC == DEVICE_DISCONNECTED_C) {
            Serial.printf("Sensor %s: disconnected\n", sensorId.c_str());
            continue;
        }

        Serial.printf("Sensor %s: %.2f C\n", sensorId.c_str(), tempC);

        if (valid > 0) {
            readingsJson += ",";
        }
        readingsJson += "{\"sensor_id\":\"";
        readingsJson += sensorId;
        readingsJson += "\",\"temperature_c\":";
        readingsJson += String(tempC, 2);
        readingsJson += "}";
        valid++;
    }

    if (valid == 0) {
        Serial.println("No valid temperature readings this cycle");
        delay(READ_INTERVAL_MS);
        return;
    }

    if (wifi_connected && WiFi.status() == WL_CONNECTED) {
        const String payload = buildPayload(readingsJson);
        if (!postReadings(payload)) {
            Serial.println("Upload failed; readings kept locally in log only");
        }
    } else {
        Serial.println("WiFi unavailable; skipping upload");
    }

    delay(READ_INTERVAL_MS);
}
