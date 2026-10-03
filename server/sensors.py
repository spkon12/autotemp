import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("autotemp")


def load_sensor_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        log.info("Sensor registry not found at %s; using ROM IDs only", path)
        return {"nodes": {}}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log.warning("Invalid sensor registry %s: %s", path, exc)
        return {"nodes": {}}

    if not isinstance(data, dict):
        log.warning("Sensor registry must be a JSON object")
        return {"nodes": {}}

    data.setdefault("nodes", {})
    return data


def enrich_reading(reading: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(reading)
    node_id = reading.get("node_id", "")
    sensor_id = reading.get("sensor_id", "")

    node_entry = registry.get("nodes", {}).get(node_id, {})
    if isinstance(node_entry, dict):
        if node_entry.get("description"):
            enriched["node_description"] = node_entry["description"]

        sensors = node_entry.get("sensors", {})
        if isinstance(sensors, dict):
            sensor_entry = sensors.get(sensor_id.upper(), sensors.get(sensor_id, {}))
            if isinstance(sensor_entry, dict):
                if sensor_entry.get("label"):
                    enriched["sensor_label"] = sensor_entry["label"]
                if sensor_entry.get("location"):
                    enriched["location"] = sensor_entry["location"]

    return enriched
