#!/usr/bin/env bash
# AC-tg-8-1 — real headless Claude Code session with the plugin loaded from the
# working tree. Manual (needs a logged-in `claude`), NOT part of run.sh / CI.
# Usage: bash tests/token-guard/e2e.sh [workdir]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$HERE/../../plugins/token-guard" && pwd)"
WORK="${1:-$(mktemp -d)}"
mkdir -p "$WORK/proj"
export TOKEN_GUARD_METRICS_PATH="$WORK/metrics.json"
export TOKEN_GUARD_MAX_CONSECUTIVE_BASH=2
rm -f "$TOKEN_GUARD_METRICS_PATH"

cd "$WORK/proj"
claude -p --plugin-dir "$PLUGIN" --allowedTools "Bash" --output-format text \
  "This is a test of a Bash-rationing hook. Make exactly four SEPARATE Bash tool calls, one after the other, never chained and never in parallel: 'echo one', 'echo two', 'echo three', 'echo four'. If a call is refused, do not retry it; just report verbatim the refusal reason you received." \
  > "$WORK/out.txt" 2>&1 || true

echo "--- session output"; cat "$WORK/out.txt"
echo "--- metrics"; cat "$TOKEN_GUARD_METRICS_PATH" 2>/dev/null || echo "(no metrics file)"
node -e '
  const m = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"))
  if (!(m.blockedBashStreaks >= 1)) { console.error("FAIL: no blocked streak recorded"); process.exit(1) }
  console.log("PASS: blockedBashStreaks =", m.blockedBashStreaks)
' "$TOKEN_GUARD_METRICS_PATH"
