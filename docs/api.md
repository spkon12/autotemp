# API

Base URL (default on TP520): `http://192.168.1.204:8080`

## POST /api/v1/readings

Store one or more temperature readings. The server timestamps each batch on receipt (UTC ISO-8601).

### Batch payload (recommended)

```json
{
  "node_id": "lab-node-1",
  "readings": [
    {"sensor_id": "28FF1234567890AB", "temperature_c": 23.45},
    {"sensor_id": "28FFABCDEF012345", "temperature_c": 24.01}
  ]
}
```

### Single-reading payload

```json
{
  "node_id": "lab-node-1",
  "sensor_id": "28FF1234567890AB",
  "temperature_c": 23.45
}
```

### Responses

- `201` — `{"stored": 2, "node_id": "lab-node-1"}`
- `400` — validation error

`sensor_id` is the DS18B20 64-bit ROM address as 16 uppercase hex characters (no separators).

## GET /api/v1/readings/recent

Returns the most recent stored readings.

Query params:

- `limit` — default 50, max 500

Example:

```bash
curl http://192.168.1.204:8080/api/v1/readings/recent?limit=10
```

## GET /health

Simple liveness check returning `{"status":"ok"}`.
