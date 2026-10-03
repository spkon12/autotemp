# Deployment

## Roles

| Machine | Role |
|---------|------|
| **TP520** (`homeberlandia`) | Receiver only — store and expose readings |
| **Windows laptop** | Build and flash ESP32 firmware over USB |

## Workflow overview

1. Clone repo on TP520 and laptop
2. Configure and start TP520 receiver
3. Configure firmware secrets on laptop
4. Build and flash ESP32 on laptop
5. Discover sensor ROM IDs from serial output or API
6. Assign physical names in TP520 `sensors.json`
7. Verify end-to-end readings
8. Physically deploy ESP32 to its monitoring location

---

## 1. TP520 — install receiver

```bash
git clone git@github.com:spkon12/autotemp.git ~/esp32-temperature-search
cd ~/esp32-temperature-search
chmod +x deploy/install-receiver.sh deploy/uninstall-receiver.sh
./deploy/install-receiver.sh user
```

This creates:

- Python venv in `server/.venv`
- Data directory `~/services/autotemp-data/`
- SQLite database `readings.db`
- Sensor registry `sensors.json` (from example)
- User systemd service `autotemp-receiver`

For a system-wide service (survives reboot without user login):

```bash
./deploy/install-receiver.sh system   # requires sudo
```

Verify:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/readings/recent
```

Uninstall:

```bash
./deploy/uninstall-receiver.sh user
```

---

## 2. Laptop — configure and flash firmware

See [firmware-build.md](firmware-build.md). Summary:

```bash
cp config/secrets.h.example firmware/autotemp/main/secrets.h
# edit WiFi + SERVER_URL + NODE_ID
cd firmware/autotemp
idf.py set-target esp32
idf.py -p COM6 build flash monitor
```

---

## 3. Assign sensor names (server-side)

After flashing, note each sensor's ROM address from serial logs or the API. Edit on TP520:

```bash
nano ~/services/autotemp-data/sensors.json
```

Example structure (also in `config/sensors.example.json`):

```json
{
  "nodes": {
    "lab-node-1": {
      "description": "Bench ESP32",
      "sensors": {
        "28BE5D210000008C": {
          "label": "bench-probe",
          "location": "workbench"
        }
      }
    }
  }
}
```

No restart required — the receiver reloads this file on each API request.

View mapped readings:

```bash
curl http://localhost:8080/api/v1/readings/recent?limit=5
```

Mapped fields appear when configured: `sensor_label`, `location`, `node_description`.

---

## 4. Confirm end-to-end

1. Serial monitor: discovered sensor IDs, temperatures, `Server response HTTP 201`
2. API: new rows at `/api/v1/readings/recent` with optional friendly names
3. ESP32 can be moved to final location once Wi-Fi and uploads are stable

---

## TP520 maintenance notes

- The receiver uses **systemd + Python venv** — no Docker required for the server.
- ESP-IDF Docker (~15 GB) is optional dev tooling only; it is not part of TP520 deployment.
- If firmware was built on the TP520 during development, `firmware/autotemp/build/` and `managed_components/` may remain (~400 MB). Safe to delete on the TP520 if you build on your laptop; they are gitignored and rebuild on the laptop when needed.
- Docker on this machine should only show Portainer unless you pull ESP-IDF again for optional containerised builds.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| WiFi fails | SSID/password in `secrets.h`; 2.4 GHz network |
| HTTP errors | TP520 IP in `SERVER_URL`; receiver running (`systemctl --user status autotemp-receiver`) |
| No sensors | Wiring, pull-up, GPIO 4; DS18B20 VDD connected |
| IDs but no labels | Edit `~/services/autotemp-data/sensors.json`; ROM address must match exactly |
| Database errors | Disk space on TP520 (`df -h /`) |

Manual test POST:

```bash
curl -X POST http://localhost:8080/api/v1/readings \
  -H 'Content-Type: application/json' \
  -d '{"node_id":"manual-test","sensor_id":"28FF000000000001","temperature_c":22.5}'
```
