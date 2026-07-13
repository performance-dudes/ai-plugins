#!/usr/bin/env bash
# Smoke test for the example plugin.
# Run from anywhere:  bash example/tests/validate.sh
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
  "commands/greet.md" \
  "workflows/greet.js" \
  "skills/run-greet/SKILL.md" \
  "agents/greeter.md" \
  "themes/performance-dudes.json" \
  "output-styles/terse.md" \
  "skills/run-greet/references/advanced-greetings.md" \
  "hooks/scripts/example-pretooluse.sh" \
  "hooks/scripts/example-posttooluse.sh" \
  ".claude/settings.json.example"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "3. JSON component files parse"
# .example templates are not loaded by Claude, but must still be valid JSON.
for j in \
  themes/performance-dudes.json \
  hooks/hooks.json.example \
  .claude/settings.json.example; do
  python3 -m json.tool "$PLUGIN_DIR/$j" >/dev/null 2>&1 && ok "$j parses" || bad "$j bad JSON"
done

note "4. Workflow script + hook scripts are syntactically valid"
node --check "$PLUGIN_DIR/workflows/greet.js" 2>/dev/null && ok "greet.js parses" || bad "greet.js syntax error"
for sh in hooks/scripts/example-pretooluse.sh hooks/scripts/example-posttooluse.sh; do
  bash -n "$PLUGIN_DIR/$sh" 2>/dev/null && ok "$sh parses" || bad "$sh syntax error"
done

note "5. Skill/agent frontmatter has name + description"
for md in skills/run-greet/SKILL.md agents/greeter.md; do
  head -10 "$PLUGIN_DIR/$md" | grep -q '^name:' && head -10 "$PLUGIN_DIR/$md" | grep -q '^description:' \
    && ok "$md frontmatter" || bad "$md missing name/description"
done

note "6. Evals present + routing scorer green on the committed sample"
for f in \
  "evals/README.md" \
  "evals/routing/ground_truth.yaml" \
  "evals/routing/predictions.example.yaml" \
  "evals/greeting/cases.yaml" \
  "evals/scripts/score_routing.py" \
  "evals/scripts/judge.py"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done
if command -v uv >/dev/null 2>&1; then
  # The deterministic routing scorer must PASS on the committed sample (exit 0).
  # A real run's misses are PLUGIN bugs — fixed at the plugin, never by editing cases.
  uv run "$PLUGIN_DIR/evals/scripts/score_routing.py" >/dev/null 2>&1 \
    && ok "score_routing.py PASS on predictions.example.yaml" \
    || bad "routing scorer failed (sample regressed, or scorer broke)"
  # judge.py needs an API key to run; here we only check it is syntactically valid.
  uv run --with pyyaml --with "anthropic>=0.40" python -c \
    "import py_compile; py_compile.compile('$PLUGIN_DIR/evals/scripts/judge.py', doraise=True)" >/dev/null 2>&1 \
    && ok "judge.py parses" || bad "judge.py syntax error"
else
  printf '  - uv not found — skipping eval scorer run (run-all stays green offline)\n'
fi

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
