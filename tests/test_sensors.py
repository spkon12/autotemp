import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

from sensors import enrich_reading, load_sensor_registry


class SensorRegistryTests(unittest.TestCase):
    def test_enrich_with_mapping(self):
        registry = {
            "nodes": {
                "lab-node-1": {
                    "description": "Bench unit",
                    "sensors": {
                        "28BE5D210000008C": {
                            "label": "bench-probe",
                            "location": "workbench",
                        }
                    },
                }
            }
        }
        row = {
            "node_id": "lab-node-1",
            "sensor_id": "28BE5D210000008C",
            "temperature_c": 18.25,
        }
        enriched = enrich_reading(row, registry)
        self.assertEqual(enriched["sensor_label"], "bench-probe")
        self.assertEqual(enriched["location"], "workbench")
        self.assertEqual(enriched["node_description"], "Bench unit")

    def test_enrich_without_mapping(self):
        row = {"node_id": "x", "sensor_id": "UNKNOWN", "temperature_c": 1.0}
        enriched = enrich_reading(row, {"nodes": {}})
        self.assertNotIn("sensor_label", enriched)

    def test_load_missing_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = load_sensor_registry(Path(tmp) / "missing.json")
            self.assertEqual(registry, {"nodes": {}})

    def test_load_invalid_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            registry = load_sensor_registry(path)
            self.assertEqual(registry, {"nodes": {}})


if __name__ == "__main__":
    unittest.main()
