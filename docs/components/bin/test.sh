#!/usr/bin/env bash
# Test for the BIN component reference (a documented gap).
# Run from anywhere:  bash docs/components/bin/test.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC="$HERE/README.md"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$DOC" ] && ok "README.md exists" || bad "README.md missing"
grep -q 'PATH' "$DOC" && ok "explains PATH behaviour" || bad "PATH not explained"
grep -q 'executable' "$DOC" && ok "documents file & format" || bad "file/format not documented"
grep -qi 'gap' "$DOC" && ok "marked as a gap (not shipped yet)" || bad "gap not marked"

[ "$fail" -eq 0 ] && echo "  BIN: PASS" || { echo "  BIN: FAIL"; exit 1; }
