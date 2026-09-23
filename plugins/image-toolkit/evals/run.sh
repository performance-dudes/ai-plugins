#!/usr/bin/env bash
# Cold-agent certification run for the image-toolkit knowledge suite.
#
#   bash evals/run.sh            # 3 trials with the skill + 1 baseline without it
#   TRIALS=5 bash evals/run.sh
#
# Cold = a fresh headless `claude -p` per trial, no tools, no skills, no MCP, started in
# an empty directory; its only image knowledge is the skill text in the prompt.
# Cheap = pinned to the production tier (MODEL, default claude-sonnet-4-6).
# With ANTHROPIC_API_KEY set, `--bare` also skips CLAUDE.md, hooks and plugins.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCORER="$HERE/scripts/score_knowledge.py"
MODEL="${MODEL:-claude-sonnet-4-6}"
TRIALS="${TRIALS:-3}"
OUT="$(mktemp -d)"
COLD_DIR="$(mktemp -d)"

flags=(-p --model "$MODEL" --tools "" --disable-slash-commands --strict-mcp-config --no-session-persistence)
[ -n "${ANTHROPIC_API_KEY:-}" ] && flags+=(--bare)

ask() {  # $1 = prompt file, $2 = answer file
  (cd "$COLD_DIR" && claude "${flags[@]}" < "$1" > "$2")
}

python3 "$SCORER" --self-test
python3 "$SCORER" --emit-prompt > "$OUT/prompt.txt"
python3 "$SCORER" --emit-prompt --baseline > "$OUT/baseline_prompt.txt"

files=()
for i in $(seq 1 "$TRIALS"); do
  echo "trial $i/$TRIALS ($MODEL, with skill)…" >&2
  ask "$OUT/prompt.txt" "$OUT/trial_$i.txt"
  files+=("$OUT/trial_$i.txt")
done
echo "baseline ($MODEL, WITHOUT skill)…" >&2
ask "$OUT/baseline_prompt.txt" "$OUT/baseline.txt"

echo "=== with skill ==="
python3 "$SCORER" --predictions "${files[@]}"
echo "=== baseline (no skill) — must fail clearly, else the suite measures priors ==="
python3 "$SCORER" --predictions "$OUT/baseline.txt"
echo "raw answers: $OUT" >&2
