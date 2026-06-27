#!/usr/bin/env bash
# Test for the MCP component.
# Run from anywhere:  bash docs/components/mcp/test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
FILE="$ROOT/example/.mcp.json.example"
fail=0
ok()  { printf '  ok  %s\n' "$1"; }
bad() { printf '  x   %s\n' "$1"; fail=1; }

[ -f "$FILE" ] && ok ".mcp.json.example exists" || bad ".mcp.json.example missing"
python3 -m json.tool "$FILE" >/dev/null 2>&1 && ok "valid JSON" || bad "invalid JSON"
grep -q '"mcpServers"' "$FILE" && ok "declares mcpServers" || bad "missing mcpServers"

[ "$fail" -eq 0 ] && echo "  MCP: PASS" || { echo "  MCP: FAIL"; exit 1; }
