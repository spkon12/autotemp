import logging
from typing import Any

from flask import Flask, jsonify, request

import config
from db import init_db, insert_readings, recent_readings
from sensors import enrich_reading, load_sensor_registry

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
log = logging.getLogger("autotemp")

app = Flask(__name__)
init_db(config.DB_PATH)


def _validate_payload(data: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")

    node_id = data.get("node_id")
    if not node_id or not isinstance(node_id, str):
        raise ValueError("node_id is required")

    readings = data.get("readings")
    if readings is None:
        sensor_id = data.get("sensor_id")
        temperature_c = data.get("temperature_c")
        if sensor_id is None or temperature_c is None:
            raise ValueError("Provide readings[] or sensor_id + temperature_c")
        readings = [{"sensor_id": sensor_id, "temperature_c": temperature_c}]

    if not isinstance(readings, list) or not readings:
        raise ValueError("readings must be a non-empty list")

    cleaned: list[dict[str, Any]] = []
    for item in readings:
        if not isinstance(item, dict):
            raise ValueError("each reading must be an object")
        sensor_id = item.get("sensor_id")
        temperature_c = item.get("temperature_c")
        if not sensor_id or not isinstance(sensor_id, str):
            raise ValueError("each reading requires sensor_id")
        if temperature_c is None:
            raise ValueError("each reading requires temperature_c")
        cleaned.append({"sensor_id": sensor_id, "temperature_c": float(temperature_c)})

    return node_id, cleaned


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/v1/readings")
def post_readings():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "invalid JSON"}), 400

    try:
        node_id, readings = _validate_payload(data)
        count = insert_readings(config.DB_PATH, node_id, readings)
    except ValueError as exc:
        log.warning("Rejected payload: %s", exc)
        return jsonify({"error": str(exc)}), 400
    except Exception:
        log.exception("Failed to store readings")
        return jsonify({"error": "internal error"}), 500

    log.info("Stored %d reading(s) from node %s", count, node_id)
    return jsonify({"stored": count, "node_id": node_id}), 201


@app.get("/api/v1/readings/recent")
def get_recent():
    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 500))
    registry = load_sensor_registry(config.SENSORS_PATH)
    rows = [enrich_reading(row, registry) for row in recent_readings(config.DB_PATH, limit=limit)]
    return jsonify({"readings": rows})


@app.get("/api/v1/sensors")
def get_sensors():
    return jsonify(load_sensor_registry(config.SENSORS_PATH))


@app.get("/")
def index():
    return (
        "<h1>autotemp receiver</h1>"
        "<p><a href='/api/v1/readings/recent'>Recent readings (JSON)</a></p>"
        "<p><a href='/api/v1/sensors'>Sensor registry (JSON)</a></p>"
        "<p>POST readings to <code>/api/v1/readings</code></p>"
    )


if __name__ == "__main__":
    log.info(
        "Starting autotemp receiver on %s:%s db=%s sensors=%s",
        config.HOST,
        config.PORT,
        config.DB_PATH,
        config.SENSORS_PATH,
    )
    app.run(host=config.HOST, port=config.PORT)
