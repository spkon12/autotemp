# esp32-temperature-search

## Overview

Minimal ESP32 connection test firmware. Prints "ESP32 alive" to serial every second at 115200 baud. GPIO 4 reserved for a future DS18B20 1-Wire bus.

## Purpose

Verify USB-serial connection and board bring-up before adding temperature sensor support.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | C |
| Framework | ESP-IDF v6.0.1, CMake |
| Dev environment | Dev Container with ESP-IDF QEMU |

## Directory Structure

```
esp32-temperature-search/
├── main/                    # connection test (ESP32 alive heartbeat)
├── ds18b20-test/            # DS18B20 temperature test (OneWire + DallasTemperature)
├── CMakeLists.txt
├── .devcontainer/
└── .vscode/
```

## Features

### Connection test (`main/`)

- Serial heartbeat: "ESP32 alive" every 1 s @ 115200 baud

### DS18B20 test (`ds18b20-test/`)

- OneWire bus on GPIO 4
- DallasTemperature library
- Prints temperature in °C every 1 s @ 115200 baud

## Dependencies

ESP-IDF toolchain (local: `C:\esp\v6.0.1\esp-idf`)

## Run / Build

Connection test (project root):

```bash
idf.py build flash monitor
```

DS18B20 test:

```bash
cd ds18b20-test
idf.py -p COM6 build flash monitor
```

## Conventions

Standard ESP-IDF layout; `.gitignore` excludes `build/`, `sdkconfig`, `managed_components/`.

## Status

Connection test and separate DS18B20 test firmware implemented.
