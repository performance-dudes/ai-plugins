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
# successor table of the reference ("## Abgeschaltete Modelle" section) and on lines of the
# script's successor map tagged `# dead-id-ok` — anywhere else they send users to a dead
# endpoint. New shut-downs from the deprecations page go into DEAD.
DEAD='gemini-2\.[05]-flash[-a-z]*image|image-preview|imagen-[34]\.0-'
REF="$PLUGIN_DIR/skills/image-toolkit/references/gemini-image-api.md"
SCRIPT="$PLUGIN_DIR/scripts/generate_image.py"
hits="$(grep -rnE --exclude-dir=__pycache__ "$DEAD" "$PLUGIN_DIR/scripts" "$PLUGIN_DIR/commands" \
  "$PLUGIN_DIR/README.md" "$PLUGIN_DIR/skills/image-toolkit/SKILL.md" 2>/dev/null | grep -v '# dead-id-ok' || true)"
[ -z "$hits" ] && ok "no shut-down model IDs in scripts/commands/README/SKILL.md" || bad "shut-down model IDs found: $hits"
outside="$(awk '/^## /{inside=($0 ~ /^## Abgeschaltete Modelle/)} !inside' "$REF" | grep -nE "$DEAD" || true)"
[ -z "$outside" ] && ok "reference: shut-down IDs only in the successor table" || bad "reference uses shut-down IDs outside the successor table: $outside"
grep -qE '^DEFAULT_MODEL = "gemini-3\.1-flash-image"' "$SCRIPT" \
  && ok "default model is gemini-3.1-flash-image (GA)" || bad "default model is not gemini-3.1-flash-image"
grep -q '"google-genai>=2\.' "$SCRIPT" \
  && ok "google-genai pinned to 2.x (Interactions API)" || bad "google-genai pin below 2.x — client.interactions missing"
grep -qE '^[^#]*client\.interactions\.create\(' "$SCRIPT" \
  && ok "script calls client.interactions.create" || bad "script does not call client.interactions.create"
grep -rqE --exclude-dir=__pycache__ 'generate_content|generateContent' "$PLUGIN_DIR/scripts" \
  && bad "scripts still use the legacy generateContent route" || ok "no legacy generateContent in scripts"

note "7. Unit: guards reject bad combinations before any paid call"
# The guards only use the stdlib at import time, so plain python3 can test them
# without uv, google-genai, Pillow or an API key.
if python3 - "$SCRIPT" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("gi", sys.argv[1])
gi = importlib.util.module_from_spec(spec); spec.loader.exec_module(gi)
M_LITE, M_FLASH, M_PRO = "gemini-3.1-flash-lite-image", "gemini-3.1-flash-image", "gemini-3-pro-image"
reject = [  # (label, callable)
    ("lite + 2K",           lambda: gi._check(M_LITE, size="2K")),
    ("flash lite + 512",    lambda: gi._check(M_LITE, size="512")),
    ("pro + 512",           lambda: gi._check(M_PRO, size="512")),
    ("pro + thinking",      lambda: gi._check(M_PRO, thinking="high")),
    ("lite + web_search",   lambda: gi._check(M_LITE, search=["web_search"])),
    ("pro + image_search",  lambda: gi._check(M_PRO, search=["image_search"])),
    ("pro + 8:1",           lambda: gi._check(M_PRO, aspect="8:1")),
    ("lite + 1:4",          lambda: gi._check(M_LITE, aspect="1:4")),
    ("shut-down id",        lambda: gi._check(next(iter(gi.SHUT_DOWN)))),
    ("out .xyz",            lambda: gi._check_out("/tmp/out.xyz")),
    ("out missing dir",     lambda: gi._check_out("/nonexistent-dir-7f3a/out.png")),
]
accept = [
    ("flash + 512 + 8:1 + image_search", lambda: gi._check(M_FLASH, "512", "high", ["image_search"], "8:1")),
    ("pro + 4K + web_search",            lambda: gi._check(M_PRO, "4K", None, ["web_search"], "21:9")),
    ("lite + 1K + minimal",              lambda: gi._check(M_LITE, "1K", "minimal", None, "16:9")),
    ("out /tmp/x.png",                   lambda: gi._check_out("/tmp/x.png")),
]
failed = 0
for label, fn in reject:
    try:
        fn(); print(f"  x    not rejected: {label}"); failed = 1
    except SystemExit:
        print(f"  ok   rejects {label}")
for label, fn in accept:
    try:
        fn(); print(f"  ok   accepts {label}")
    except SystemExit as e:
        print(f"  x    wrongly rejected {label}: {e}"); failed = 1
sys.exit(failed)
PY
then :; else bad "guard unit tests"; fi

note "8. Eval harness is sound (runs the scorer, not the model)"
if python3 "$PLUGIN_DIR/evals/scripts/score_knowledge.py" --self-test; then
  ok "knowledge eval self-test passed"
else
  bad "knowledge eval self-test failed"
fi
bash -n "$PLUGIN_DIR/evals/run.sh" 2>/dev/null && ok "evals/run.sh syntax" || bad "evals/run.sh syntax"

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
