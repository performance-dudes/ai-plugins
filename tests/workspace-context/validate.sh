#!/usr/bin/env bash
# Smoke test for the public workspace-context plugin.
set -uo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../plugins/workspace-context" && pwd)"
MARKET_DIR="$(cd "$PLUGIN_DIR/../.." && pwd)"
fail=0

note() { printf '\n=== %s ===\n' "$1"; }
ok() { printf '  ✔ %s\n' "$1"; }
bad() { printf '  x %s\n' "$1"; fail=1; }

note "1. Manifest and marketplace"
if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR" >/dev/null 2>&1 \
    && ok "plugin manifest validates" || bad "plugin manifest is invalid"
  claude plugin validate "$MARKET_DIR" >/dev/null 2>&1 \
    && ok "marketplace manifest validates" || bad "marketplace manifest is invalid"
else
  printf '  - claude CLI not found — skipping CLI validation\n'
fi

note "2. Component files"
for f in \
  ".claude-plugin/plugin.json" \
  "README.md" \
  "skills/workspace-context/SKILL.md" \
  "skills/workspace-context/reference/AGENTS.md.template" \
  "skills/workspace-context/reference/reindex-workspace.json.template" \
  "skills/workspace-context/reference/reindex-workspace.sh.template" \
  "skills/workspace-context/reference/reindex-workspace.ps1.template"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "3. Static syntax and content"
python3 - "$PLUGIN_DIR/.claude-plugin/plugin.json" \
  "$PLUGIN_DIR/skills/workspace-context/reference/reindex-workspace.json.template" <<'PY' \
  && ok "JSON files parse" || bad "JSON file is invalid"
import json
import sys

for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as handle:
        json.load(handle)
PY

bash -n "$PLUGIN_DIR/skills/workspace-context/reference/reindex-workspace.sh.template" \
  && ok "Bash template parses" || bad "Bash template has a syntax error"

head -12 "$PLUGIN_DIR/skills/workspace-context/SKILL.md" | grep -q '^name:' \
  && head -12 "$PLUGIN_DIR/skills/workspace-context/SKILL.md" | grep -q '^description:' \
  && ok "skill frontmatter is present" || bad "skill frontmatter is incomplete"

grep -q 'disable-model-invocation: true' \
  "$PLUGIN_DIR/skills/workspace-context/SKILL.md" \
  && ok "skill remains explicit-invocation only" \
  || bad "skill invocation guard is missing"

grep -q 'additionalContext' \
  "$PLUGIN_DIR/skills/workspace-context/reference/reindex-workspace.sh.template" \
  && grep -q 'completion counts' \
  "$PLUGIN_DIR/skills/workspace-context/reference/reindex-workspace.sh.template" \
  && ok "hook success and failure contracts are documented in code" \
  || bad "hook contract is incomplete"

note "4. Public hygiene"
# Hygiene: no client names or internal identifiers in the public plugin.
#
# The terms live in hygiene-check.py as SHA-256 prefixes, not as text. The earlier
# version listed them here as string-concatenated literals so the check would not
# match itself — which also hid them from grep, from this check, and from a
# reviewing agent, while leaving them plainly readable to anyone opening the file.
if python3 "$(dirname "$0")/hygiene-check.py" "$PLUGIN_DIR"; then
  ok "no client names or internal identifiers in the public plugin"
else
  bad "forbidden term(s) found — see above"
fi

note "5. Eval harness is sound (runs the scorer, not the model)"
python3 "$PLUGIN_DIR/evals/scripts/score_judgment.py" --self-test 2>&1 | sed 's/^/  /' \
  && ok "eval self-test passed" || bad "eval self-test failed"
python3 "$PLUGIN_DIR/evals/scripts/score_judgment.py" --emit-prompt 2>/dev/null \
  | grep -q "Setup contract" && ok "prompt injects the real SKILL.md" \
  || bad "prompt does not contain the skill — harness would measure itself"

note "Result"
if [ "$fail" -eq 0 ]; then
  echo "  ALL CHECKS PASSED"
else
  echo "  FAILURES ABOVE"
fi
exit "$fail"
