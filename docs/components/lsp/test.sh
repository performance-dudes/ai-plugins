#!/usr/bin/env bash
# Test for the LSP component.
# Run from anywhere:  bash docs/components/lsp/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/.lsp.json.example"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok ".lsp.json.example exists" || bad ".lsp.json.example missing"
python3 -m json.tool "$FILE" >/dev/null 2>&1 && ok "valid JSON" || bad "invalid JSON"

[ "$fail" -eq 0 ] && echo "  LSP: PASS" || { echo "  LSP: FAIL"; exit 1; }
