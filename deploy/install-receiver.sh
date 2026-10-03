#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_DIR="$REPO_ROOT/server"
DATA_DIR="${HOME}/services/autotemp-data"
MODE="${1:-user}"

echo "==> Preparing data directory at $DATA_DIR"
mkdir -p "$DATA_DIR"
if [[ ! -f "$DATA_DIR/sensors.json" ]]; then
  cp "$REPO_ROOT/config/sensors.example.json" "$DATA_DIR/sensors.json"
  echo "    Created $DATA_DIR/sensors.json from example (edit to assign sensor names)"
fi

echo "==> Creating Python virtualenv"
python3 -m venv "$SERVER_DIR/.venv"
"$SERVER_DIR/.venv/bin/pip" install --upgrade pip
"$SERVER_DIR/.venv/bin/pip" install -r "$SERVER_DIR/requirements.txt"

if [[ "$MODE" == "system" ]]; then
  echo "==> Installing system-wide systemd unit (requires sudo)"
  sudo cp "$REPO_ROOT/deploy/autotemp-receiver.service" /etc/systemd/system/autotemp-receiver.service
  sudo systemctl daemon-reload
  sudo systemctl enable autotemp-receiver.service
  sudo systemctl restart autotemp-receiver.service
  sudo systemctl --no-pager status autotemp-receiver.service | head -15
elif [[ "$MODE" == "user" ]]; then
  echo "==> Installing user systemd unit (no sudo)"
  mkdir -p "${HOME}/.config/systemd/user"
  sed "s|%h|${HOME}|g" "$REPO_ROOT/deploy/autotemp-receiver.user.service" \
    > "${HOME}/.config/systemd/user/autotemp-receiver.service"
  systemctl --user daemon-reload
  systemctl --user enable autotemp-receiver.service
  systemctl --user restart autotemp-receiver.service
  systemctl --user --no-pager status autotemp-receiver.service | head -15
  echo
  echo "For boot without login: sudo loginctl enable-linger ${USER}"
else
  echo "Usage: $0 [user|system]" >&2
  exit 1
fi

echo
echo "Recent readings: http://$(hostname -I | awk '{print $1}'):8080/api/v1/readings/recent"
