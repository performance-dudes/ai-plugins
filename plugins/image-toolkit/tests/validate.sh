#!/usr/bin/env bash
# Smoke test for the image-toolkit plugin. Run from anywhere:
#   bash image-toolkit/tests/validate.sh
# Validates structure + syntax of every shipped file. No network, no API key,
# no ImageMagick/uv needed — pure static checks so it can gate CI.
set -uo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0
note() { printf '\n=== %s ===\n' "$1"; }
ok()   { printf '  ok   %s\n' "$1"; }
bad()  { printf '  x    %s\n' "$1"; fail=1; }

note "1. plugin.json valid JSON"
python3 -m json.tool "$PLUGIN_DIR/.claude-plugin/plugin.json" >/dev/null 2>&1 \
  && ok "plugin.json parses" || bad "plugin.json invalid JSON"
if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR" >/dev/null 2>&1 && ok "claude plugin validate" || bad "claude plugin validate failed"
fi

note "2. Component files present"
for f in \
  ".claude-plugin/plugin.json" \
  "commands/image.md" "commands/image-doctor.md" \
  "skills/image-toolkit/SKILL.md" \
  "skills/image-toolkit/references/imagemagick.md" \
  "skills/image-toolkit/references/gemini-image-api.md" \
  "scripts/generate_image.py" "scripts/doctor.sh" \
  "README.md"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "3. Shell scripts: syntax + executable"
while IFS= read -r f; do
  bash -n "$f" 2>/dev/null || { bad "${f#$PLUGIN_DIR/} (syntax)"; continue; }
  [ -x "$f" ] && ok "${f#$PLUGIN_DIR/} (+x)" || bad "${f#$PLUGIN_DIR/} (not executable)"
done < <(find "$PLUGIN_DIR/scripts" -name '*.sh' | sort)

note "4. Python script compiles + has PEP-723 header"
if python3 -m py_compile "$PLUGIN_DIR/scripts/generate_image.py" 2>/dev/null; then
  ok "generate_image.py compiles"
else
  bad "generate_image.py syntax error"
fi
head -8 "$PLUGIN_DIR/scripts/generate_image.py" | grep -q '# /// script' \
  && ok "generate_image.py has PEP-723 header" || bad "generate_image.py missing PEP-723 header"

note "5. Frontmatter has required keys"
for md in commands/image.md commands/image-doctor.md; do
  head -6 "$PLUGIN_DIR/$md" | grep -q '^description:' && ok "$md (description)" || bad "$md missing description"
done
head -16 "$PLUGIN_DIR/skills/image-toolkit/SKILL.md" | grep -q '^name:' \
  && head -16 "$PLUGIN_DIR/skills/image-toolkit/SKILL.md" | grep -q '^description:' \
  && ok "SKILL.md (name+description)" || bad "SKILL.md missing name/description"

note "6. Gemini models: GA only, no shut-down IDs"
# Shut down per ai.google.dev/gemini-api/docs/deprecations. They may appear ONLY in the
# successor table of the reference ("## Abgeschaltete Modelle" section) — anywhere else
# they would send users to a dead endpoint.
DEAD='gemini-2\.5-flash-image|gemini-3\.1-flash-image-preview|gemini-3-pro-image-preview|imagen-[34]\.0-'
REF="$PLUGIN_DIR/skills/image-toolkit/references/gemini-image-api.md"
hits="$(grep -rnE --exclude-dir=__pycache__ "$DEAD" "$PLUGIN_DIR/scripts" "$PLUGIN_DIR/commands" "$PLUGIN_DIR/README.md" 2>/dev/null || true)"
[ -z "$hits" ] && ok "no shut-down model IDs in scripts/commands/README" || bad "shut-down model IDs found: $hits"
outside="$(awk '/^## /{inside=($0 ~ /^## Abgeschaltete Modelle/)} !inside' "$REF" | grep -nE "$DEAD" || true)"
[ -z "$outside" ] && ok "reference: shut-down IDs only in the successor table" || bad "reference uses shut-down IDs outside the successor table: $outside"
grep -qE '^DEFAULT_MODEL = "gemini-3\.1-flash-image"' "$PLUGIN_DIR/scripts/generate_image.py" \
  && ok "default model is gemini-3.1-flash-image (GA)" || bad "default model is not gemini-3.1-flash-image"
grep -q '"google-genai>=2\.' "$PLUGIN_DIR/scripts/generate_image.py" \
  && ok "google-genai pinned to 2.x (Interactions API)" || bad "google-genai pin below 2.x — client.interactions missing"
grep -q 'interactions\.create' "$PLUGIN_DIR/scripts/generate_image.py" \
  && ok "script uses the Interactions API" || bad "script does not call interactions.create"

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
