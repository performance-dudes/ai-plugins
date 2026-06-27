#!/usr/bin/env bash
# Test for the COMMAND component.
# Run from anywhere:  bash docs/components/command/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/commands/greet.md"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok "greet.md exists" || bad "greet.md missing"
head -10 "$FILE" | grep -q '^description:' && ok "has description frontmatter" || bad "missing description frontmatter"
grep -q 'greet.js' "$FILE" && ok "invokes the bundled workflow" || bad "does not invoke greet.js"

[ "$fail" -eq 0 ] && echo "  COMMAND: PASS" || { echo "  COMMAND: FAIL"; exit 1; }
