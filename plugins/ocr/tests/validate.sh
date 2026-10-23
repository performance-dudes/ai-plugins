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
  # Parse as the Workflow runtime does: body of an async function (top-level return/await).
  # Plain `node --check` fails on Node 24 (ESM detection rejects top-level return).
  node -e 'const s=require("fs").readFileSync(process.argv[1],"utf8").replace(/^export\s+/gm,"");new (Object.getPrototypeOf(async function(){}).constructor)(s)' "$PLUGIN_DIR/workflows/ocr.js" 2>/dev/null && ok "ocr.js parses" || bad "ocr.js syntax error"
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

skip() { printf '  --   %s (skipped)\n' "$1"; }

note "9. Text-layer font round-trips Cyrillic + Umlauts (macOS font)"
if ! command -v uv >/dev/null 2>&1; then skip "uv absent"
elif [ ! -f "${OCR_FONT_FILE:-/System/Library/Fonts/Helvetica.ttc}" ]; then skip "no Helvetica.ttc (not macOS)"
else
  uv run -q --with pymupdf python - "$PLUGIN_DIR/scripts" <<'PY' 2>/dev/null && ok "Cyrillic + Umlauts survive embed + subset + extract" || bad "text-layer font loses script"
import sys; sys.path.insert(0, sys.argv[1])
import pymupdf, searchbar
doc = pymupdf.open(); page = doc.new_page()
s = "Пикочна киселина / Uric acid äöüÄÖÜß € „Zoll“ – §"
page.insert_text((20, 50), s, fontsize=12, render_mode=3, **searchbar.font_kwargs())
doc.subset_fonts()
doc = pymupdf.open("pdf", doc.tobytes())
assert doc[0].get_text().strip() == s, doc[0].get_text()
PY
fi

note "10. --redo replaces an invisible layer safely (auge mocked)"
if ! command -v uv >/dev/null 2>&1; then skip "uv absent"
elif [ ! -f "${OCR_FONT_FILE:-/System/Library/Fonts/Helvetica.ttc}" ]; then skip "no Helvetica.ttc (not macOS)"
else
  rtmp="$(mktemp -d)"
  uv run -q --with pymupdf python - "$PLUGIN_DIR/scripts" "$rtmp" <<'PY' 2>/dev/null && ok "rotated page cleared, links kept once, image pixels identical, empty OCR aborts" || bad "--redo replace unsafe"
import sys; sys.path.insert(0, sys.argv[1])
from pathlib import Path
import pymupdf, searchbar
tmp = Path(sys.argv[2])
NEW = [{"text": "NEU", "x": 0.1, "y": 0.5, "height": 0.02}]

def make(path, rotate):
    doc = pymupdf.open(); page = doc.new_page(width=595, height=842)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 40), 0); pix.set_rect(pix.irect, (200, 30, 30))
    page.insert_image(pymupdf.Rect(50, 50, 545, 792), pixmap=pix)
    for y in (100, 400, 700):
        page.insert_text((60, y), f"ALT{y}", fontsize=12, render_mode=3, fontname="helv")
    page.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(60, 60, 200, 80), "uri": "https://example.org"})
    # outside the page box (e.g. scanner-app watermark links): redaction keeps it -> must not be duplicated
    page.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(60, 900, 200, 920), "uri": "https://example.org/out"})
    page.set_rotation(rotate)
    doc.save(str(path)); doc.close()

searchbar.auge_lines = lambda _png: NEW
for rot in (0, 90):
    p = tmp / f"r{rot}.pdf"; make(p, rot)
    before = searchbar._image_digests(pymupdf.open(str(p)))
    assert searchbar.pdf_has_only_invisible_text(p)
    searchbar.add_textlayer(p, replace=True)
    d = pymupdf.open(str(p))
    assert d[0].get_text().split() == ["NEU"], (rot, d[0].get_text())
    assert len(d[0].get_links()) == 2, (rot, "link lost or duplicated", d[0].get_links())
    assert searchbar._image_digests(d) == before, (rot, "image changed")

p = tmp / "empty.pdf"; make(p, 0); raw = p.read_bytes()
searchbar.auge_lines = lambda _png: []
try:
    searchbar.add_textlayer(p, replace=True); raise SystemExit("no abort on empty OCR")
except RuntimeError:
    pass
assert p.read_bytes() == raw and not list(tmp.glob("*.tmp.pdf")), "file touched after abort"
PY
  rm -rf "$rtmp"
fi

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
