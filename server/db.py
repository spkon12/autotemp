import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL,
    node_id TEXT NOT NULL,
    sensor_id TEXT NOT NULL,
    temperature_c REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_readings_received_at ON readings(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_readings_node_sensor ON readings(node_id, sensor_id);
"""


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connect(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def insert_readings(db_path: Path, node_id: str, readings: list[dict[str, Any]]) -> int:
    received_at = datetime.now(timezone.utc).isoformat()
    rows = [
        (received_at, node_id, item["sensor_id"], float(item["temperature_c"]))
        for item in readings
    ]
    with connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO readings (received_at, node_id, sensor_id, temperature_c) VALUES (?, ?, ?, ?)",
            rows,
        )
    return len(rows)


def recent_readings(db_path: Path, limit: int = 50) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            SELECT id, received_at, node_id, sensor_id, temperature_c
            FROM readings
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]
