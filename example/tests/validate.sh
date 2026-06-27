#!/usr/bin/env bash
# Smoke test for the example plugin.
# Run from anywhere:  bash example/tests/validate.sh
# Exits non-zero on the first failure so it can gate CI.
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKET_DIR="$(cd "$PLUGIN_DIR/.." && pwd)"
fail=0

note() { printf '\n=== %s ===\n' "$1"; }
ok()   { printf '  ✔ %s\n' "$1"; }
bad()  { printf '  x %s\n' "$1"; fail=1; }

note "1. Manifest + marketplace validate"
claude plugin validate "$PLUGIN_DIR" >/dev/null 2>&1 && ok "plugin.json valid"        || bad "plugin.json invalid"
claude plugin validate "$MARKET_DIR" >/dev/null 2>&1 && ok "marketplace.json valid"   || bad "marketplace.json invalid"

note "2. Component files present"
for f in \
  "commands/greet.md" \
  "workflows/greet.js" \
  "skills/run-greet/SKILL.md" \
  "agents/greeter.md" \
  "themes/performance-dudes.json" \
  "output-styles/terse.md"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "3. JSON component files parse"
for j in themes/performance-dudes.json; do
  python3 -m json.tool "$PLUGIN_DIR/$j" >/dev/null 2>&1 && ok "$j parses" || bad "$j bad JSON"
done

note "4. Workflow script is syntactically valid JS"
node --check "$PLUGIN_DIR/workflows/greet.js" 2>/dev/null && ok "greet.js parses" || bad "greet.js syntax error"

note "5. Skill/agent frontmatter has name + description"
for md in skills/run-greet/SKILL.md agents/greeter.md; do
  head -10 "$PLUGIN_DIR/$md" | grep -q '^name:' && head -10 "$PLUGIN_DIR/$md" | grep -q '^description:' \
    && ok "$md frontmatter" || bad "$md missing name/description"
done

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
