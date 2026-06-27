#!/usr/bin/env bash
# Test for the OUTPUT-STYLE component.
# Run from anywhere:  bash docs/components/output-style/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/output-styles/terse.md"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok "terse.md exists" || bad "terse.md missing"
head -10 "$FILE" | grep -q '^name:' && ok "has name frontmatter" || bad "missing name frontmatter"
head -10 "$FILE" | grep -q '^description:' && ok "has description frontmatter" || bad "missing description frontmatter"

[ "$fail" -eq 0 ] && echo "  OUTPUT-STYLE: PASS" || { echo "  OUTPUT-STYLE: FAIL"; exit 1; }
