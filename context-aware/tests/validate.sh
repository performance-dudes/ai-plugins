#!/usr/bin/env bash
# Smoke test for the context-aware plugin.
# Run from anywhere:  bash context-aware/tests/validate.sh
# Exits non-zero on the first failure so it can gate CI.
set -uo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKET_DIR="$(cd "$PLUGIN_DIR/.." && pwd)"
fail=0

note() { printf '\n=== %s ===\n' "$1"; }
ok()   { printf '  ✔ %s\n' "$1"; }
bad()  { printf '  x %s\n' "$1"; fail=1; }

note "1. Manifest + marketplace validate"
if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR" >/dev/null 2>&1 && ok "plugin.json valid"      || bad "plugin.json invalid"
  claude plugin validate "$MARKET_DIR" >/dev/null 2>&1 && ok "marketplace.json valid" || bad "marketplace.json invalid"
else
  printf '  - claude CLI not found — skipping validate\n'
fi

note "2. plugin.json is lean (context-mode is a workspace-level dependency, not bundled)"
python3 - "$PLUGIN_DIR/.claude-plugin/plugin.json" <<'PY' && ok "no per-plugin mcpServers; context-mode required via workspace" || bad "plugin.json should NOT bundle an MCP server"
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if "mcpServers" not in d else 1)
PY

note "3. Component files present"
for f in \
  "commands/context-aware.md" \
  "commands/context-aware-doctor.md" \
  "workflows/context-aware-demo.js" \
  "skills/context-aware/SKILL.md" \
  "skills/context-aware/references/ctx-tool-surface.md" \
  "skills/context-aware/references/patterns.md" \
  "skills/context-aware/references/bundling-context-mode.md" \
  "skills/context-aware/references/agent-recipes.md" \
  "agents/context-scout.md" \
  "agents/context-synthesizer.md" \
  "scripts/doctor.sh"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "4. Workflow script is syntactically valid JS"
if command -v node >/dev/null 2>&1; then
  node --check "$PLUGIN_DIR/workflows/context-aware-demo.js" 2>/dev/null && ok "context-aware-demo.js parses" || bad "context-aware-demo.js syntax error"
else
  printf '  - node not found — skipping JS check\n'
fi

note "5. Skill/agent frontmatter has name + description"
for md in \
  "skills/context-aware/SKILL.md" \
  "agents/context-scout.md" \
  "agents/context-synthesizer.md"; do
  head -12 "$PLUGIN_DIR/$md" | grep -q '^name:' && head -12 "$PLUGIN_DIR/$md" | grep -q '^description:' \
    && ok "$md frontmatter" || bad "$md missing name/description"
done

note "6. Agents allowlist a context-mode (ctx_*) namespace"
for md in "agents/context-scout.md" "agents/context-synthesizer.md"; do
  grep -q 'context-mode__\*' "$PLUGIN_DIR/$md" && ok "$md wires ctx_*" || bad "$md does not allowlist ctx_*"
done

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
