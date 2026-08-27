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

note "6. Part.from_text is called with a keyword (google-genai is keyword-only)"
# Part.from_text ist keyword-only (def from_text(cls, *, text: str)); ein
# positionaler Aufruf bricht nur den --edit-Pfad, weil --prompt Part nie anfasst.
# Kommentarzeilen vorher rauswerfen: der erklaerende Kommentar ueber dem Aufruf
# zitiert die falsche Form zwangsläufig und wuerde den Test sonst umdrehen.
gi="$PLUGIN_DIR/scripts/generate_image.py"
if grep -E '^[^#]*Part\.from_text\(' "$gi" | grep -qv 'from_text(text='; then
  bad "Part.from_text called positionally (TypeError im --edit-Pfad)"
else
  ok "no positional Part.from_text call"
fi
grep -qE '^[^#]*Part\.from_text\(text=' "$gi" \
  && ok "Part.from_text(text=…) present" || bad "Part.from_text(text=…) missing"

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
