# autotemp

Lab temperature monitoring: ESP32 + DS18B20 sensors → TP520 receiver → SQLite.

## How it fits together

```
[Laptop]  build/flash ESP32 over USB
    ↓ Wi-Fi
[TP520]   receive → timestamp → SQLite → HTTP API
```

- **TP520** runs the receiver (Flask + SQLite + systemd). No ESP-IDF needed in normal operation.
- **Laptop** builds and flashes firmware. Sensor friendly names live on the TP520, not in firmware.

## Repository layout

| Path | Purpose |
|------|---------|
| `firmware/autotemp/` | Production firmware — multi-sensor, Wi-Fi, HTTP upload |
| `firmware/connection-test/` | USB/serial heartbeat diagnostic |
| `server/` | Flask receiver API + SQLite storage |
| `config/` | Example secrets and sensor registry |
| `deploy/` | TP520 install/uninstall scripts |
| `tests/` | Server API tests |
| `docs/` | Hardware, API, deployment, firmware build |

## Quick start

### 1. TP520 — receiver

```bash
git clone git@github.com:spkon12/autotemp.git ~/esp32-temperature-search
cd ~/esp32-temperature-search
./deploy/install-receiver.sh user
curl http://localhost:8080/api/v1/readings/recent
```

### 2. Laptop — firmware

```bash
cp config/secrets.h.example firmware/autotemp/main/secrets.h
# edit WiFi, SERVER_URL, NODE_ID
cd firmware/autotemp
idf.py set-target esp32
idf.py -p COM6 build flash monitor
```

### 3. Name sensors on TP520

Copy ROM IDs from serial output into `~/services/autotemp-data/sensors.json` (see `config/sensors.example.json`).

## Documentation

| Guide | Contents |
|-------|----------|
| [docs/deployment.md](docs/deployment.md) | Full bench-to-deploy workflow |
| [docs/firmware-build.md](docs/firmware-build.md) | Laptop build/flash, reproducibility |
| [docs/hardware.md](docs/hardware.md) | Wiring and sensor IDs |
| [docs/api.md](docs/api.md) | HTTP API reference |

## Requirements

- **TP520:** Python 3.10+
- **Laptop:** ESP-IDF v6.x, USB serial
- **Hardware:** ESP32, DS18B20(s), 4.7 kΩ pull-up on GPIO 4
