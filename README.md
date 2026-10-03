# autotemp

Lab temperature monitoring: ESP32 + DS18B20 sensors → TP520 receiver → SQLite.

## Repository layout

| Path | Purpose |
|------|---------|
| `firmware/autotemp/` | Production firmware — multi-sensor, Wi-Fi, HTTP upload |
| `firmware/connection-test/` | Original ESP32 heartbeat test (preserved) |
| `server/` | Flask receiver API + SQLite storage |
| `config/` | Example secrets and node configuration |
| `deploy/` | TP520 systemd install scripts |
| `tests/` | Server API tests |
| `docs/` | Hardware, API, and deployment guides |

## Quick start

**TP520 receiver**

```bash
./deploy/install-receiver.sh
curl http://localhost:8080/api/v1/readings/recent
```

**ESP32 firmware**

```bash
cp config/secrets.h.example firmware/autotemp/main/secrets.h
# edit secrets.h
cd firmware/autotemp
idf.py set-target esp32
idf.py -p COM6 build flash monitor
```

See [docs/deployment.md](docs/deployment.md) for the full bench-to-deploy walkthrough.

## API

Documented in [docs/api.md](docs/api.md). Default endpoint: `POST /api/v1/readings`.

## Requirements

- ESP-IDF v6.x + Arduino component (firmware)
- Python 3.10+ (receiver)
- DS18B20 on GPIO 4 with 4.7 kΩ pull-up
