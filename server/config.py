import os
from pathlib import Path


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


HOST = _env("AUTOTEMP_HOST", "0.0.0.0")
PORT = int(_env("AUTOTEMP_PORT", "8080"))
DB_PATH = Path(_env("AUTOTEMP_DB_PATH", "/home/batthumb/services/autotemp-data/readings.db"))
SENSORS_PATH = Path(_env("AUTOTEMP_SENSORS_PATH", "/home/batthumb/services/autotemp-data/sensors.json"))
LOG_LEVEL = _env("AUTOTEMP_LOG_LEVEL", "INFO")
