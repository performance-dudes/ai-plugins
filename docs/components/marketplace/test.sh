#!/usr/bin/env bash
# Test for the MARKETPLACE component.
# Run from anywhere:  bash docs/components/marketplace/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/.claude-plugin/marketplace.json"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok "marketplace.json exists" || bad "marketplace.json missing"
python3 -m json.tool "$FILE" >/dev/null 2>&1 && ok "valid JSON" || bad "invalid JSON"
for field in name owner plugins; do
  grep -q "\"$field\"" "$FILE" && ok "has \"$field\"" || bad "missing \"$field\""
done
grep -q '"example"' "$FILE" && ok "lists the example plugin" || bad "example plugin not listed"

[ "$fail" -eq 0 ] && echo "  MARKETPLACE: PASS" || { echo "  MARKETPLACE: FAIL"; exit 1; }
