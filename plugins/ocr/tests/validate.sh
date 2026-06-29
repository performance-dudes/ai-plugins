#!/usr/bin/env bash
# Smoke test for the ocr plugin. Run from anywhere:
#   bash ocr/tests/validate.sh
# Validates structure + syntax of every shipped file, and runs deterministic
# unit tests that need no OCR engine, no models and no network:
#   - ocr.py session grouping (scanner prefix)
#   - anwenden.py dry-run plans correctly and moves NOTHING
# Exits non-zero on the first failure so it can gate CI.
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
  "commands/ocr.md" "commands/ocr-apply.md" "commands/ocr-searchable.md" "commands/ocr-doctor.md" \
  "workflows/ocr.js" \
  "skills/document-ocr/SKILL.md" \
  "scripts/ocr.py" "scripts/klassifiziere.py" "scripts/anwenden.py" \
  "scripts/durchsuchbar.py" "scripts/searchbar.py" "scripts/classify_prompt.md" "scripts/doctor.sh"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "3. Workflow script is valid JavaScript"
if command -v node >/dev/null 2>&1; then
  node --check "$PLUGIN_DIR/workflows/ocr.js" 2>/dev/null && ok "ocr.js parses" || bad "ocr.js syntax error"
else
  ok "node absent — skipped (install node >=20 to check)"
fi

note "4. Shell scripts: syntax + executable"
while IFS= read -r f; do
  bash -n "$f" 2>/dev/null || { bad "${f#$PLUGIN_DIR/} (syntax)"; continue; }
  [ -x "$f" ] && ok "${f#$PLUGIN_DIR/} (+x)" || bad "${f#$PLUGIN_DIR/} (not executable)"
done < <(find "$PLUGIN_DIR/scripts" -name '*.sh' | sort)

note "5. Python scripts compile"
while IFS= read -r f; do
  python3 -m py_compile "$f" 2>/dev/null && ok "${f#$PLUGIN_DIR/}" || bad "${f#$PLUGIN_DIR/} (syntax)"
done < <(find "$PLUGIN_DIR/scripts" -name '*.py' | sort)

note "6. Frontmatter has required keys"
for md in commands/ocr.md commands/ocr-apply.md commands/ocr-searchable.md commands/ocr-doctor.md; do
  head -6 "$PLUGIN_DIR/$md" | grep -q '^description:' && ok "$md (description)" || bad "$md missing description"
done
head -8 "$PLUGIN_DIR/skills/document-ocr/SKILL.md" | grep -q '^name:' \
  && head -8 "$PLUGIN_DIR/skills/document-ocr/SKILL.md" | grep -q '^description:' \
  && ok "SKILL.md (name+description)" || bad "SKILL.md missing name/description"

note "7. ocr.py session grouping (deterministic unit test)"
python3 - "$PLUGIN_DIR/scripts/ocr.py" <<'PY' && ok "session_key groups scanner pages" || bad "session grouping wrong"
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("ocrmod", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert m.session_key(Path("20260101120000_001.jpg")) == "20260101120000"
assert m.session_key(Path("20260101120000_002.jpg")) == "20260101120000"
assert m.session_key(Path("holiday letter.pdf")) == "holiday_letter"
PY

note "8. anwenden.py dry-run: photo-vs-document threshold, moves NOTHING"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/src" "$tmp/ocrdir" "$tmp/dest"
printf 'fake-scan' > "$tmp/src/doc1.jpg"      # document: has OCR text -> searchable PDF
printf 'fake-photo' > "$tmp/src/photo1.jpg"   # photo: no/low OCR text -> stays image
# document gets an OCR .txt above the MIN_DOC_CHARS threshold; photo gets none.
printf -- '--- page: doc1.jpg ---\nThis is a real document with plenty of recognized text content.\n' > "$tmp/ocrdir/doc1.txt"
cat > "$tmp/ocrdir/_vorschlag.json" <<JSON
[{"session":"doc1","dokumenttyp":"Letter","person":"unbekannt","datum":"2026","sprechender_name":"2026_Letter","zielordner":"Letters/","konfidenz":"hoch","ist_muell":false,"begruendung":"test"},
 {"session":"photo1","dokumenttyp":"Photo","person":"unbekannt","datum":"2026","sprechender_name":"2026_Photo","zielordner":"Private/","konfidenz":"niedrig","ist_muell":false,"begruendung":"test"}]
JSON
out="$(python3 "$PLUGIN_DIR/scripts/anwenden.py" "$tmp/ocrdir" --src "$tmp/src" --ziel-root "$tmp/dest" 2>&1)"
if printf '%s' "$out" | grep -q 'DRY-RUN' \
   && printf '%s' "$out" | grep -q '2026_Letter.pdf' \
   && printf '%s' "$out" | grep -q 'searchable PDF' \
   && printf '%s' "$out" | grep -q '2026_Photo.jpg' \
   && printf '%s' "$out" | grep -q 'stays image' \
   && [ -f "$tmp/src/doc1.jpg" ] && [ -f "$tmp/src/photo1.jpg" ] \
   && [ -z "$(find "$tmp/dest" -type f)" ]; then
  ok "document -> PDF, photo -> image; nothing changed"
else
  bad "dry-run behaved unexpectedly: $out"
fi

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
