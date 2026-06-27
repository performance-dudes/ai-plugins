#!/usr/bin/env bash
# Smoke test for the transcribe plugin. Run from anywhere:
#   bash transcribe/tests/validate.sh
# Validates structure + syntax of every shipped file, and runs the deterministic
# chunker against a synthetic transcript (no audio, no network, no models).
# Exits non-zero on the first failure so it can gate CI.
set -uo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0
note() { printf '\n=== %s ===\n' "$1"; }
ok()   { printf '  ok   %s\n' "$1"; }
bad()  { printf '  x    %s\n' "$1"; fail=1; }

note "1. plugin.json valid JSON"
if python3 -m json.tool "$PLUGIN_DIR/.claude-plugin/plugin.json" >/dev/null 2>&1; then
  ok "plugin.json parses"
else
  bad "plugin.json invalid JSON"
fi
# Optional, only if the Claude CLI is present:
if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR" >/dev/null 2>&1 && ok "claude plugin validate" || bad "claude plugin validate failed"
fi

note "2. Component files present"
for f in \
  ".claude-plugin/plugin.json" \
  "commands/transcribe.md" \
  "commands/transcribe-doctor.md" \
  "workflows/transcribe.js" \
  "skills/transcription/SKILL.md" \
  "scripts/run_pipeline.sh" \
  "scripts/merge.py" \
  "scripts/prepare_chunks.py" \
  "scripts/doctor.sh"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done

note "3. Workflow script is valid JavaScript"
if command -v node >/dev/null 2>&1; then
  node --check "$PLUGIN_DIR/workflows/transcribe.js" 2>/dev/null && ok "transcribe.js parses" || bad "transcribe.js syntax error"
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
for md in commands/transcribe.md commands/transcribe-doctor.md; do
  head -6 "$PLUGIN_DIR/$md" | grep -q '^description:' && ok "$md (description)" || bad "$md missing description"
done
head -8 "$PLUGIN_DIR/skills/transcription/SKILL.md" | grep -q '^name:' \
  && head -8 "$PLUGIN_DIR/skills/transcription/SKILL.md" | grep -q '^description:' \
  && ok "SKILL.md (name+description)" || bad "SKILL.md missing name/description"

note "7. Chunker unit test (synthetic transcript, deterministic)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/x_merged_raw.json" <<'JSON'
[
  {"start": 0,   "end": 10,  "speaker": "SPEAKER_00", "text": "Guten Morgen, ich bin Anna."},
  {"start": 11,  "end": 20,  "speaker": "SPEAKER_01", "text": "Und ich bin Bob, hallo."},
  {"start": 21,  "end": 95,  "speaker": "SPEAKER_00", "text": "Lass uns anfangen mit dem Thema."},
  {"start": 96,  "end": 130, "speaker": "SPEAKER_01", "text": "Klingt gut, bis spaeter."}
]
JSON
run_py() { if command -v uv >/dev/null 2>&1; then uv run "$1" "${@:2}"; else python3 "$1" "${@:2}"; fi; }
# Force two chunks with a tiny budget; map applied.
summary="$(run_py "$PLUGIN_DIR/scripts/prepare_chunks.py" "$tmp/x_merged_raw.json" \
  --map SPEAKER_00=Anna SPEAKER_01=Bob --out "$tmp/out" --max-chars 40 2>/dev/null)"
manifest="$tmp/out/chunks/manifest.json"
if [ -f "$manifest" ]; then
  ok "manifest.json written"
  python3 - "$manifest" <<'PY' && ok "manifest anchors correct" || bad "manifest anchors wrong"
import json, sys
m = json.load(open(sys.argv[1]))
turns = sum(c["turn_count"] for c in m)
assert turns == 4, f"turn sum {turns} != 4"
assert m[0]["first_speaker"] == "Anna", m[0]["first_speaker"]
assert m[0]["first_ts"] == "00:00:00", m[0]["first_ts"]
assert all(c["min_output_chars"] == int(c["input_chars"]*0.85) for c in m)
assert len(m) >= 2, "expected the tiny budget to force >=2 chunks"
PY
  # mapping must have replaced the raw speaker ids in the chunk text
  grep -q "Anna:" "$tmp/out/chunks/chunk_00.txt" && ok "speaker map applied" || bad "speaker map not applied"
else
  bad "manifest.json not produced ($summary)"
fi

note "Result"
if [ "$fail" -eq 0 ]; then echo "  ALL CHECKS PASSED"; else echo "  FAILURES ABOVE"; fi
exit "$fail"
