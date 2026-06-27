#!/usr/bin/env bash
# Test for the THEME component.
# Run from anywhere:  bash docs/components/theme/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/themes/performance-dudes.json"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok "theme file exists" || bad "theme file missing"
python3 -m json.tool "$FILE" >/dev/null 2>&1 && ok "valid JSON" || bad "invalid JSON"

[ "$fail" -eq 0 ] && echo "  THEME: PASS" || { echo "  THEME: FAIL"; exit 1; }
