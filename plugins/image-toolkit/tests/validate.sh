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
  "skills/image-toolkit/references/azure-image-api.md" \
  "scripts/generate_image.py" "scripts/doctor.sh" \
  "README.md"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "2b. No secrets or environment-specific values committed"
# The plugin must ship zero credentials and zero endpoints: keys, resource
# hostnames and deployment URLs all come from the environment at run time.
# Placeholders (<your-resource>, ${AZURE_*}) are what the docs are allowed to show.
leaks=0
while IFS= read -r hit; do
  bad "possible secret/endpoint literal: $hit"
  leaks=1
done < <(
  grep -rInE \
    -e '[A-Za-z0-9_-]*\.(openai\.azure\.com|services\.ai\.azure\.com)' \
    -e 'AIza[0-9A-Za-z_-]{20,}' \
    -e '(api[_-]?key|API[_-]?KEY)[[:space:]]*[=:][[:space:]]*["'"'"']?[A-Za-z0-9]{24,}' \
    "$PLUGIN_DIR" --exclude-dir=__pycache__ 2>/dev/null \
    | grep -v '<your-resource>' \
    | grep -v '\${AZURE' \
    | grep -v 'grep -rInE'
)
[ "$leaks" -eq 0 ] && ok "no credential or endpoint literals found"

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

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
