#!/usr/bin/env bash
# token-guard test suite (SPEC-token-guard). Offline, zero-dep, node >= 18.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
P="$REPO/plugins/token-guard"
echo "--- config-valid"
node -e 'JSON.parse(require("fs").readFileSync(process.argv[1]));JSON.parse(require("fs").readFileSync(process.argv[2]))' "$P/.claude-plugin/plugin.json" "$P/hooks/hooks.json"
for f in "$P"/hooks/*.mjs "$P"/hooks/lib/*.mjs; do node --check "$f"; done
if command -v claude >/dev/null 2>&1; then claude plugin validate "$P" >/dev/null && echo "  plugin validate ok"; fi
echo "--- script-run + hook-behavior"
node --test "$HERE"/*.test.mjs
echo "--- eval (deterministic, no model): offload detector pass^3"
if command -v uv >/dev/null 2>&1; then
  uv run --quiet "$P/evals/scripts/score_offload.py" 3
else
  echo "  - uv not found — skipping offload eval (run-all stays green offline)"
fi
