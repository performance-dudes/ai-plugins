#!/usr/bin/env bash
# Test for the SKILL component.
# Run from anywhere:  bash docs/components/skill/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/skills/run-greet/SKILL.md"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok "SKILL.md exists" || bad "SKILL.md missing"
head -10 "$FILE" | grep -q '^name:' && ok "has name frontmatter" || bad "missing name frontmatter"
head -10 "$FILE" | grep -q '^description:' && ok "has description frontmatter" || bad "missing description frontmatter"
grep -q 'greet.js' "$FILE" && ok "calls the bundled workflow" || bad "does not call greet.js"

[ "$fail" -eq 0 ] && echo "  SKILL: PASS" || { echo "  SKILL: FAIL"; exit 1; }
