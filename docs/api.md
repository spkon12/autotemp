# API

Base URL (default on TP520): `http://192.168.1.204:8080`

## POST /api/v1/readings

Store one or more temperature readings. The server timestamps each batch on receipt (UTC ISO-8601).

### Batch payload (recommended)

```json
{
  "node_id": "lab-node-1",
  "readings": [
    {"sensor_id": "28BE5D210000008C", "temperature_c": 23.45}
  ]
}
```

### Single-reading payload

```json
{
  "node_id": "lab-node-1",
  "sensor_id": "28BE5D210000008C",
  "temperature_c": 23.45
}
```

### Responses

- `201` — `{"stored": 1, "node_id": "lab-node-1"}`
- `400` — validation error

`sensor_id` is the DS18B20 64-bit ROM address as 16 uppercase hex characters (no separators).

## GET /api/v1/readings/recent

Returns the most recent stored readings. When `sensors.json` is configured on the TP520, each row may include:

- `sensor_label` — friendly name
- `location` — physical location
- `node_description` — node description

Query params:

- `limit` — default 50, max 500

Example response:

```json
{
  "readings": [
    {
      "id": 6,
      "received_at": "2026-10-03T22:21:10.027341+00:00",
      "node_id": "lab-node-1",
      "node_description": "Bench ESP32",
      "sensor_id": "28BE5D210000008C",
      "sensor_label": "bench-probe",
      "location": "workbench",
      "temperature_c": 18.25
    }
  ]
}
```

## GET /api/v1/sensors

Returns the current sensor registry (`sensors.json` on the TP520).

## GET /health

Simple liveness check returning `{"status":"ok"}`.
