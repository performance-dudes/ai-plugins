#!/usr/bin/env bash
# Test for the HOOKS component.
# Run from anywhere:  bash docs/components/hooks/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SCRIPT="$ROOT/example/hooks/scripts/example-pretooluse.sh"
CONF="$ROOT/example/hooks/hooks.json.example"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$SCRIPT" ] && ok "hook script exists" || bad "hook script missing"

# AC-HOOKS-1-2: runs in isolation and exits 0
if echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | bash "$SCRIPT" >/dev/null 2>&1; then
  ok "hook exits 0 (allow) in isolation"
else
  bad "hook did not exit 0"
fi

[ -f "$CONF" ] && python3 -m json.tool "$CONF" >/dev/null 2>&1 && ok "hooks.json.example is valid JSON" || bad "hooks.json.example invalid/missing"

[ "$fail" -eq 0 ] && echo "  HOOKS: PASS" || { echo "  HOOKS: FAIL"; exit 1; }
