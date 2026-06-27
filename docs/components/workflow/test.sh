#!/usr/bin/env bash
# Test for the WORKFLOW component.
# Run from anywhere:  bash docs/components/workflow/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/workflows/greet.js"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok "greet.js exists" || bad "greet.js missing"
node --check "$FILE" 2>/dev/null && ok "valid JavaScript" || bad "JS syntax error"
grep -q 'export const meta' "$FILE" && ok "defines meta" || bad "missing meta"
grep -q 'greeting' "$FILE" && ok "returns a greeting" || bad "no greeting in return"

[ "$fail" -eq 0 ] && echo "  WORKFLOW: PASS" || { echo "  WORKFLOW: FAIL"; exit 1; }
