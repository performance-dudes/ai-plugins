#!/usr/bin/env bash
# Test for the MONITORS component.
# Run from anywhere:  bash docs/components/monitors/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CONF="$ROOT/example/monitors/monitors.json.example"
SCRIPT="$ROOT/example/monitors/scripts/heartbeat.sh"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$CONF" ] && python3 -m json.tool "$CONF" >/dev/null 2>&1 && ok "monitors.json.example is valid JSON" || bad "monitors.json.example invalid/missing"
[ -f "$SCRIPT" ] && ok "heartbeat.sh exists" || bad "heartbeat.sh missing"
head -1 "$SCRIPT" | grep -q '^#!' && ok "heartbeat.sh has a shebang" || bad "heartbeat.sh missing shebang"

[ "$fail" -eq 0 ] && echo "  MONITORS: PASS" || { echo "  MONITORS: FAIL"; exit 1; }
