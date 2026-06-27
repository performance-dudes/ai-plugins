#!/usr/bin/env bash
# Test for the SUBAGENT component.
# Run from anywhere:  bash docs/components/subagent/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/agents/greeter.md"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok "greeter.md exists" || bad "greeter.md missing"
head -12 "$FILE" | grep -q '^name:' && ok "has name frontmatter" || bad "missing name frontmatter"
head -12 "$FILE" | grep -q '^description:' && ok "has description frontmatter" || bad "missing description frontmatter"
grep -q '^tools:' "$FILE" && ok "declares a tools allow-list" || bad "missing tools allow-list"

[ "$fail" -eq 0 ] && echo "  SUBAGENT: PASS" || { echo "  SUBAGENT: FAIL"; exit 1; }
