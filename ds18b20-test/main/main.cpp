#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

static const gpio_num_t DS18B20_GPIO = GPIO_NUM_4;

OneWire oneWire(DS18B20_GPIO);
DallasTemperature sensors(&oneWire);

void setup()
{
    Serial.begin(115200);
    sensors.begin();
    Serial.printf("DS18B20 devices found: %u\n", sensors.getDeviceCount());
}

void loop()
{
    sensors.requestTemperatures();
    const float temp_c = sensors.getTempCByIndex(0);

    if (temp_c == DEVICE_DISCONNECTED_C) {
        Serial.println("Temperature: sensor disconnected");
    } else {
        Serial.printf("Temperature: %.2f °C\n", temp_c);
    }

    delay(1000);
}
