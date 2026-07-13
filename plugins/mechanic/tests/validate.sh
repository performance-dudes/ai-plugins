#!/usr/bin/env bash
# Smoke test for the mechanic plugin.
# Run from anywhere:  bash mechanic/tests/validate.sh
# Exits non-zero on the first failure so it can gate CI.
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKET_DIR="$(cd "$PLUGIN_DIR/../.." && pwd)"   # plugins/<name> -> repo root (marketplace root)
fail=0

note() { printf '\n=== %s ===\n' "$1"; }
ok()   { printf '  ✔ %s\n' "$1"; }
bad()  { printf '  x %s\n' "$1"; fail=1; }

note "1. Manifest + marketplace validate"
if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR" >/dev/null 2>&1 && ok "plugin.json valid"        || bad "plugin.json invalid"
  claude plugin validate "$MARKET_DIR" >/dev/null 2>&1 && ok "marketplace.json valid"   || bad "marketplace.json invalid"
else
  printf '  - claude CLI not found — skipping validate (run-all stays green offline)\n'
fi

note "2. Component files present"
for f in \
  ".claude-plugin/plugin.json" \
  "agents/errand.md" \
  "agents/mechanic.md" \
  "README.md"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "3. plugin.json parses"
python3 -m json.tool "$PLUGIN_DIR/.claude-plugin/plugin.json" >/dev/null 2>&1 \
  && ok "plugin.json parses" || bad "plugin.json bad JSON"

note "4. Agent frontmatter has name + description + model pin"
for md in agents/errand.md agents/mechanic.md; do
  # extract the YAML frontmatter block (between the first two '---' fences),
  # so a long folded description can't push 'model:' out of a fixed head window.
  fm="$(awk 'NR==1&&/^---/{f=1;next} f&&/^---/{exit} f' "$PLUGIN_DIR/$md")"
  printf '%s\n' "$fm" | grep -q '^name:' \
    && printf '%s\n' "$fm" | grep -q -E '^ *description:' \
    && printf '%s\n' "$fm" | grep -q '^model:' \
    && ok "$md frontmatter (name/description/model)" || bad "$md missing name/description/model"
done

note "5. Evals present + routing scorer green on the committed sample"
for f in \
  "evals/README.md" \
  "evals/routing/ground_truth.yaml" \
  "evals/routing/predictions.example.yaml" \
  "evals/scripts/score_routing.py"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done
if command -v uv >/dev/null 2>&1; then
  # The deterministic routing scorer must PASS on the committed sample (exit 0).
  # A real run's misses are PLUGIN bugs — fixed at the descriptions, never by
  # editing cases. See evals/README.md ("the one rule").
  uv run "$PLUGIN_DIR/evals/scripts/score_routing.py" >/dev/null 2>&1 \
    && ok "score_routing.py PASS on predictions.example.yaml" \
    || bad "routing scorer failed (sample regressed, or scorer broke)"
else
  printf '  - uv not found — skipping eval scorer run (run-all stays green offline)\n'
fi

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
