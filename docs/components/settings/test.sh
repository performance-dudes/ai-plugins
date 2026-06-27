#!/usr/bin/env bash
# Test for the SETTINGS component reference (a documented gap).
# Run from anywhere:  bash docs/components/settings/test.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC="$HERE/README.md"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$DOC" ] && ok "README.md exists" || bad "README.md missing"
grep -q 'settings.json' "$DOC" && ok "documents settings.json" || bad "settings.json not documented"
grep -q 'subagentStatusLine' "$DOC" && ok "documents the status line" || bad "subagentStatusLine not documented"
grep -qi 'gap' "$DOC" && ok "marked as a gap (not shipped yet)" || bad "gap not marked"

[ "$fail" -eq 0 ] && echo "  SETTINGS: PASS" || { echo "  SETTINGS: FAIL"; exit 1; }
