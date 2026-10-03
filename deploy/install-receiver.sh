#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_DIR="$REPO_ROOT/server"
DATA_DIR="/home/batthumb/services/autotemp-data"
SERVICE_NAME="autotemp-receiver.service"

echo "==> Preparing data directory at $DATA_DIR"
mkdir -p "$DATA_DIR"

echo "==> Creating Python virtualenv"
python3 -m venv "$SERVER_DIR/.venv"
"$SERVER_DIR/.venv/bin/pip" install --upgrade pip
"$SERVER_DIR/.venv/bin/pip" install -r "$SERVER_DIR/requirements.txt"

echo "==> Installing systemd unit"
sudo cp "$REPO_ROOT/deploy/$SERVICE_NAME" "/etc/systemd/system/$SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "==> Receiver status"
sudo systemctl --no-pager status "$SERVICE_NAME" | head -15
echo
echo "Recent readings: http://$(hostname -I | awk '{print $1}'):8080/api/v1/readings/recent"
