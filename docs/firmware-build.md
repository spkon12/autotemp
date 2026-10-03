# Firmware build and flash (development laptop)

ESP32 firmware is built and flashed from a **development machine** (normally your Windows laptop over USB). The TP520 only runs the receiver — it does not need ESP-IDF or Docker for normal operation.

## Requirements

- [ESP-IDF v6.x](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/) installed locally (e.g. `C:\esp\v6.0.1\esp-idf` on Windows)
- USB serial driver for your ESP32 board (CP210x, CH340, etc.)
- DS18B20 on GPIO 4 with 4.7 kΩ pull-up

Reproducibility is provided by:

- `firmware/autotemp/dependencies.lock` — pinned component versions
- `firmware/autotemp/sdkconfig.defaults` — project defaults
- `firmware/autotemp/main/idf_component.yml` — Arduino-ESP32 dependency
- Vendored OneWire and DallasTemperature in `firmware/autotemp/components/`

## Configure secrets (not committed)

```bash
cp config/secrets.h.example firmware/autotemp/main/secrets.h
```

Edit `secrets.h`:

- `WIFI_SSID` / `WIFI_PASSWORD` — lab Wi-Fi
- `SERVER_URL` — TP520 receiver, e.g. `http://192.168.1.204:8080/api/v1/readings`
- `NODE_ID` — unique name for this ESP32, e.g. `lab-node-1`

Do **not** put sensor friendly names in firmware. The ESP32 sends ROM addresses; names are assigned on the TP520 (see [deployment.md](deployment.md)).

## Build and flash

**Windows (PowerShell or ESP-IDF CMD):**

```bash
cd firmware/autotemp
idf.py set-target esp32
idf.py -p COM6 build flash monitor
```

Replace `COM6` with your serial port.

**Linux/macOS:**

```bash
cd firmware/autotemp
idf.py set-target esp32
idf.py -p /dev/ttyUSB0 build flash monitor
```

First build downloads managed components and compiles the ESP-IDF + Arduino stack — expect a long wait (tens of minutes on a modest machine). Subsequent edits to `main.cpp` or `secrets.h` rebuild in under a couple of minutes if you keep the `build/` directory.

## Discover sensor ROM IDs

With serial monitor running after flash, look for lines like:

```
DS18B20 devices found: 1
  [0] 28BE5D210000008C
```

Copy these hex IDs into `~/services/autotemp-data/sensors.json` on the TP520 (see deployment guide).

## Diagnostic firmware

| Project | Purpose |
|---------|---------|
| `firmware/connection-test/` | USB/serial heartbeat — "ESP32 alive" every second |
| `firmware/autotemp/` | Production — sensors, Wi-Fi, upload |

Build diagnostic projects the same way (`cd` into the project folder, then `idf.py build flash monitor`).

## Optional: Dev Container

`.devcontainer/` provides an optional ESP-IDF Docker environment for VS Code/Cursor. It is **not** required for deployment and is **not** used on the TP520 in normal operation.
