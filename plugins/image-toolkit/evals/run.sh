#!/usr/bin/env bash
# Cold-agent certification run for the image-toolkit knowledge suite.
#
#   bash evals/run.sh                  # 3 trials with the skill + 1 forced-choice baseline
#   TRIALS=5 BASELINE_MAX=0.65 MIN_DISCRIMINATING=15 bash evals/run.sh
#
# Cold: a fresh headless `claude -p` per trial in an empty directory, no tools, no skills,
# no MCP, no settings sources (so no CLAUDE.md, memory, hooks or plugins) and a one-line
# system prompt. Measured: ~460 input tokens of context before the task.
# Cheap: pinned to the production tier (MODEL, default claude-sonnet-4-6).
#
# Exit 1 if the skill run is not certified (every task in every trial), OR the no-skill
# baseline scores above BASELINE_MAX, OR fewer than MIN_DISCRIMINATING tasks separate skill
# from baseline — then the suite would measure priors, not the skill. Why these defaults:
# evals/README.md, "Schranken".
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCORER="$HERE/scripts/score_knowledge.py"
MODEL="${MODEL:-claude-sonnet-4-6}"
TRIALS="${TRIALS:-3}"
BASELINE_MAX="${BASELINE_MAX:-0.65}"
MIN_DISCRIMINATING="${MIN_DISCRIMINATING:-15}"
OUT="$(mktemp -d)"
COLD_DIR="$(mktemp -d)"

flags=(-p --model "$MODEL" --tools "" --disable-slash-commands --strict-mcp-config
       --setting-sources "" --system-prompt "You answer questions precisely."
       --no-session-persistence)

ask() {  # $1 = prompt file, $2 = answer file
  (cd "$COLD_DIR" && claude "${flags[@]}" < "$1" > "$2") || { echo "claude -p failed ($1)" >&2; exit 2; }
  [ -s "$2" ] || { echo "empty answer from claude -p ($1)" >&2; exit 2; }
}

python3 "$SCORER" --self-test || exit 2
python3 "$SCORER" --emit-prompt > "$OUT/prompt.txt"
python3 "$SCORER" --emit-prompt --baseline > "$OUT/baseline_prompt.txt"

echo "environment: $(claude --version 2>/dev/null) · model $MODEL · trials $TRIALS · isolation: no tools/skills/MCP/settings sources · baseline gate ≤ $BASELINE_MAX · ≥ $MIN_DISCRIMINATING discriminating"

files=()
for i in $(seq 1 "$TRIALS"); do
  echo "trial $i/$TRIALS ($MODEL, with skill)…" >&2
  ask "$OUT/prompt.txt" "$OUT/trial_$i.txt"
  files+=("$OUT/trial_$i.txt")
done
echo "baseline ($MODEL, WITHOUT skill, forced choice)…" >&2
ask "$OUT/baseline_prompt.txt" "$OUT/baseline.txt"

echo "=== with skill (vs. baseline) ==="
python3 "$SCORER" --predictions "${files[@]}" --baseline-predictions "$OUT/baseline.txt" \
  --min-discriminating "$MIN_DISCRIMINATING"; cert=$?
echo "=== baseline gate ==="
python3 "$SCORER" --baseline-predictions "$OUT/baseline.txt" --max-accuracy "$BASELINE_MAX" > /dev/null; gate=$?
[ "$gate" -eq 0 ] && echo "baseline below gate" || echo "baseline ABOVE gate"
echo "raw answers: $OUT" >&2
[ "$cert" -eq 0 ] && [ "$gate" -eq 0 ]
