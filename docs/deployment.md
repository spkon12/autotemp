# Deployment

End-to-end setup for a fresh TP520 and ESP32.

## 1. Clone on TP520

```bash
cd ~
git clone git@github.com:spkon12/autotemp.git esp32-temperature-search
```

## 2. Install receiver service

```bash
cd ~/esp32-temperature-search
chmod +x deploy/install-receiver.sh
./deploy/install-receiver.sh
```

Verify:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/readings/recent
```

The service is enabled for reboot via `autotemp-receiver.service`.

Data is stored in SQLite at `/home/batthumb/services/autotemp-data/readings.db`.

## 3. Configure ESP32 firmware

```bash
cp config/secrets.h.example firmware/autotemp/main/secrets.h
# Edit WiFi credentials, SERVER_URL, NODE_ID
```

Build and flash (from a machine with ESP-IDF v6.x):

```bash
cd firmware/autotemp
idf.py set-target esp32
idf.py -p /dev/ttyUSB0 build flash monitor
```

On Windows use `COM6` (or your port) instead of `/dev/ttyUSB0`.

## 4. Confirm end-to-end

1. Serial monitor shows discovered sensor IDs and temperatures.
2. Serial shows `Server response HTTP 201` after each upload cycle.
3. Browser or curl shows new rows at `/api/v1/readings/recent`.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| WiFi fails | SSID/password in `secrets.h`; 2.4 GHz network |
| HTTP errors | TP520 IP in `SERVER_URL`; receiver running (`systemctl status autotemp-receiver`) |
| No sensors | Wiring, pull-up, GPIO 4; power to DS18B20 VDD |
| Empty recent API | ESP32 not reaching server; test with manual curl POST |

Manual test POST:

```bash
curl -X POST http://localhost:8080/api/v1/readings \
  -H 'Content-Type: application/json' \
  -d '{"node_id":"manual-test","sensor_id":"28FF000000000001","temperature_c":22.5}'
```
