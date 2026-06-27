#!/usr/bin/env bash
# Test for the MANIFEST component.
# Run from anywhere:  bash docs/components/manifest/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/.claude-plugin/plugin.json"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

# AC-MANIFEST-1-1: file exists
[ -f "$FILE" ] && ok "plugin.json exists" || bad "plugin.json missing"

# AC-MANIFEST-1-2: valid JSON
python3 -m json.tool "$FILE" >/dev/null 2>&1 && ok "valid JSON" || bad "invalid JSON"

# AC-MANIFEST-1-3: has required name field
grep -q '"name"' "$FILE" && ok 'has "name" field' || bad 'missing "name" field'

[ "$fail" -eq 0 ] && echo "  MANIFEST: PASS" || { echo "  MANIFEST: FAIL"; exit 1; }
