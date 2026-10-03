# autotemp

ESP32 firmware for automated temperature sensing with a DS18B20 on GPIO 4.

## Projects

| Path | Purpose |
|------|---------|
| `/` (root) | Connection test — prints `ESP32 alive` every second |
| `ds18b20-test/` | DS18B20 temperature read via OneWire + DallasTemperature |

## Requirements

- ESP-IDF v6.x
- ESP32 dev board (CP210x USB serial)
- DS18B20 on GPIO 4 with 4.7kΩ pull-up to 3.3V

## Build & flash

Connection test:

```bash
idf.py set-target esp32
idf.py -p COM6 build flash monitor
```

DS18B20 test:

```bash
cd ds18b20-test
idf.py set-target esp32
idf.py -p COM6 build flash monitor
```

Serial: **115200 baud**.
