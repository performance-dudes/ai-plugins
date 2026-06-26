#!/usr/bin/env bash
# Example background monitor: a persistent process whose stdout lines become events.
# Demo only — emits a heartbeat every 30s. Real monitors tail logs, poll a deploy, etc.
set -euo pipefail
while true; do
  echo "[example plugin] heartbeat"
  sleep 30
done
