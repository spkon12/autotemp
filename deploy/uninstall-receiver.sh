#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-user}"

if [[ "$MODE" == "system" ]]; then
  echo "==> Removing system-wide autotemp-receiver service (requires sudo)"
  sudo systemctl disable --now autotemp-receiver.service 2>/dev/null || true
  sudo rm -f /etc/systemd/system/autotemp-receiver.service
  sudo systemctl daemon-reload
elif [[ "$MODE" == "user" ]]; then
  echo "==> Removing user autotemp-receiver service"
  systemctl --user disable --now autotemp-receiver.service 2>/dev/null || true
  rm -f "${HOME}/.config/systemd/user/autotemp-receiver.service"
  systemctl --user daemon-reload
else
  echo "Usage: $0 [user|system]" >&2
  exit 1
fi

echo "Done. Database and sensors.json in ~/services/autotemp-data were not deleted."
