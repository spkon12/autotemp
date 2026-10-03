import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

import app as autotemp_app
import config
import db
class ApiTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.sensors_path = Path(self._tmpdir.name) / "sensors.json"
        config.DB_PATH = self.db_path
        config.SENSORS_PATH = self.sensors_path
        db.init_db(self.db_path)
        autotemp_app.app.config["TESTING"] = True
        self.client = autotemp_app.app.test_client()

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "ok")

    def test_post_single_reading(self):
        payload = {
            "node_id": "test-node",
            "sensor_id": "28FF1234567890AB",
            "temperature_c": 21.5,
        }
        resp = self.client.post(
            "/api/v1/readings",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["stored"], 1)

    def test_post_batch_and_recent(self):
        payload = {
            "node_id": "test-node",
            "readings": [
                {"sensor_id": "28FF111111111111", "temperature_c": 20.0},
                {"sensor_id": "28FF222222222222", "temperature_c": 21.0},
            ],
        }
        resp = self.client.post(
            "/api/v1/readings",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["stored"], 2)

        recent = self.client.get("/api/v1/readings/recent?limit=10")
        self.assertEqual(recent.status_code, 200)
        rows = recent.get_json()["readings"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["node_id"], "test-node")

    def test_recent_includes_sensor_labels(self):
        self.sensors_path.write_text(
            json.dumps(
                {
                    "nodes": {
                        "test-node": {
                            "sensors": {
                                "28FF111111111111": {"label": "probe-a", "location": "shelf"}
                            }
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        payload = {
            "node_id": "test-node",
            "sensor_id": "28FF111111111111",
            "temperature_c": 20.0,
        }
        self.client.post(
            "/api/v1/readings",
            data=json.dumps(payload),
            content_type="application/json",
        )
        recent = self.client.get("/api/v1/readings/recent?limit=1")
        row = recent.get_json()["readings"][0]
        self.assertEqual(row["sensor_label"], "probe-a")
        self.assertEqual(row["location"], "shelf")


if __name__ == "__main__":
    unittest.main()
