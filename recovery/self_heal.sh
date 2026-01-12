#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="fastapi-app"

log() {
  echo "[self-heal] $(date -u +"%Y-%m-%dT%H:%M:%SZ") $*"
}

log "Starting recovery sequence for ${SERVICE_NAME}"

if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl restart "${SERVICE_NAME}"
  log "Issued systemctl restart ${SERVICE_NAME}"
else
  log "systemctl not found; no-op. Plug your restart logic here."
fi

log "Recovery sequence completed"
