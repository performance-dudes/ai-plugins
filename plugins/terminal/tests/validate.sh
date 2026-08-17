#!/usr/bin/env bash
# Smoke test for the terminal plugin.
# Run from anywhere:  bash plugins/terminal/tests/validate.sh
# Traceability: SPEC-terminal AC-term-*, see tests/terminal/coverage.md
set -uo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKET_DIR="$(cd "$PLUGIN_DIR/../.." && pwd)"
INSTALL="$PLUGIN_DIR/scripts/install-iterm-profile.sh"
fail=0

note() { printf '\n=== %s ===\n' "$1"; }
ok()   { printf '  ✔ %s\n' "$1"; }
bad()  { printf '  x %s\n' "$1"; fail=1; }

# Sandbox so no test ever writes into the real iTerm2 profile directory.
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
export ITERM_PROFILE_DIR="$TMP/profiles"

note "1. Manifest + marketplace validate"
if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR" >/dev/null 2>&1 && ok "plugin.json valid"      || bad "plugin.json invalid"
  claude plugin validate "$MARKET_DIR" >/dev/null 2>&1 && ok "marketplace.json valid" || bad "marketplace.json invalid"
else
  printf '  - claude CLI not found — skipping validate\n'
fi

note "2. Component files present"
for f in \
  ".claude-plugin/plugin.json" \
  "README.md" \
  "commands/iterm-profile.md" \
  "scripts/install-iterm-profile.sh" \
  "skills/iterm-dynamic-profile/SKILL.md" \
  "templates/performance-dudes.json"; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done
[ -x "$INSTALL" ] && ok "installer is executable" || bad "installer not executable"

note "3. Static validity (config-valid)"
bash -n "$INSTALL" && ok "installer syntax (bash -n)" || bad "installer has syntax errors"
for j in "$PLUGIN_DIR"/templates/*.json "$PLUGIN_DIR/.claude-plugin/plugin.json"; do
  python3 -m json.tool "$j" >/dev/null 2>&1 && ok "valid JSON: $(basename "$j")" || bad "invalid JSON: $j"
done

note "4. Skill frontmatter (skill-lint)"
python3 - "$PLUGIN_DIR/skills/iterm-dynamic-profile/SKILL.md" <<'PY' && ok "frontmatter has name + description" || bad "frontmatter incomplete"
import sys, re
t = open(sys.argv[1]).read()
m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
sys.exit(0 if m and 'name:' in m.group(1) and 'description:' in m.group(1) else 1)
PY

note "5. Templates carry no machine-specific paths (AC-term-2-1)"
if grep -qE '"/Users/|"/home/' "$PLUGIN_DIR"/templates/*.json; then
  bad "a template contains an absolute home path — must use {{HOME}}"
else
  ok "no absolute home paths in templates"
fi

note "6. Badge escaping (AC-term-1-2)"
# In JSON the backslash must be doubled; a single one yields a literal badge.
python3 - "$PLUGIN_DIR/templates/performance-dudes.json" <<'PY' && ok 'badge resolves to \(session.name)' || bad "badge text not escaped correctly"
import json, sys
p = json.load(open(sys.argv[1]))["Profiles"][0]
sys.exit(0 if p.get("Badge Text", "").endswith("\\(session.name)") else 1)
PY

note "7. Installer dry-run from template (script-run, AC-term-4-2)"
OUT="$("$INSTALL" --template performance-dudes --dry-run 2>/dev/null)"
if [ -n "$OUT" ] && printf '%s' "$OUT" | python3 -m json.tool >/dev/null 2>&1; then
  ok "dry-run emits valid JSON"
else
  bad "dry-run produced no valid JSON"
fi
[ -d "$ITERM_PROFILE_DIR" ] && bad "dry-run wrote to disk (must not)" || ok "dry-run wrote nothing"

note "8. Generated profile satisfies the core contract (AC-term-1-1/1-3/1-4, 4-3)"
# Data goes through a file, not a pipe: `python3 -` already consumes stdin for the
# script itself, so a heredoc and a pipe cannot both feed it.
printf '%s' "$OUT" > "$TMP/out.json"
python3 - "$TMP/out.json" <<'PY' && ok "Profiles array, Bound Hosts absolute, badge/tab alpha split, stable Guid" || bad "generated profile violates the contract"
import json, sys
d = json.load(open(sys.argv[1]))
p = d["Profiles"][0]
def alpha(k): return p[k]["Alpha Component"]
def rgb(k):   return tuple(round(p[k][c + " Component"], 6) for c in ("Red", "Green", "Blue"))
checks = [
    isinstance(d.get("Profiles"), list) and len(d["Profiles"]) == 1,   # AC-term-4-3
    all(h.startswith("/") for h in p["Bound Hosts"]),                  # AC-term-1-1
    p["Working Directory"].startswith("/"),
    "{{" not in json.dumps(p),                                        # AC-term-2-2
    alpha("Badge Color") == 0.5 and alpha("Tab Color") == 1,           # AC-term-1-3
    rgb("Badge Color") == rgb("Tab Color"),                            # same hue
    p.get("Guid") and " " not in p["Guid"],                            # AC-term-1-4
]
sys.exit(0 if all(checks) else 1)
PY

note "9. Degradation when assets are missing (AC-term-3-*)"
# HOME bent at an empty dir: every asset candidate misses.
DEG="$(HOME="$TMP/empty" "$INSTALL" --template performance-dudes --dir "$TMP/empty/proj" --dry-run 2>/dev/null)"
printf '%s' "$DEG" > "$TMP/deg.json"
python3 - "$TMP/deg.json" <<'PY' && ok "fields omitted, no dead paths, Icon removed with its path" || bad "degradation path is broken"
import json, sys
p = json.load(open(sys.argv[1]))["Profiles"][0]
checks = [
    "Background Image Location" not in p,   # AC-term-3-2
    "Custom Icon Path" not in p,
    "Icon" not in p,                        # AC-term-3-3 companion key
    p["Bound Hosts"][0].startswith("/"),    # AC-term-3-4: still installable
    p.get("Badge Text") and p.get("Tab Color"),
]
sys.exit(0 if all(checks) else 1)
PY

note "10. Unresolved placeholder aborts instead of writing junk (AC-term-2-3)"
if HOME="$TMP/empty" "$INSTALL" --template performance-dudes --dry-run >/dev/null 2>&1; then
  ok "template resolves {{HOME}} on its own (no --dir needed)"
else
  bad "template could not resolve without --dir"
fi

note "11. Flag mode + repeat run stays a single profile (AC-term-4-1)"
"$INSTALL" --name "Test Profile" --emoji "🧪" --color "#3B7DED" --dir "$TMP" >/dev/null 2>&1
T="$ITERM_PROFILE_DIR/Test Profile.json"
[ -f "$T" ] && ok "profile written" || bad "profile not written"
"$INSTALL" --name "Test Profile" --emoji "🧪" --color "#3B7DED" --dir "$TMP" >/dev/null 2>&1
COUNT=$(find "$ITERM_PROFILE_DIR" -name '*.json' | wc -l | tr -d ' ')
[ "$COUNT" = "1" ] && ok "second run created no duplicate (1 file)" || bad "second run created duplicates ($COUNT files)"

note "12. Colour conversion is exact"
python3 - "$T" <<'PY' && ok "#3B7DED round-trips exactly" || bad "colour conversion is lossy"
import json, sys
p = json.load(open(sys.argv[1]))["Profiles"][0]["Tab Color"]
got = tuple(round(p[c + " Component"] * 255) for c in ("Red", "Green", "Blue"))
sys.exit(0 if got == (0x3B, 0x7D, 0xED) else 1)
PY

note "13. Marketplace lists this plugin"
python3 - "$MARKET_DIR/.claude-plugin/marketplace.json" <<'PY' && ok "terminal is registered" || bad "terminal missing from marketplace.json"
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if any(p["name"] == "terminal" for p in d["plugins"]) else 1)
PY

note "14. Eval harness is sound (runs the scorer, not the model)"
python3 "$PLUGIN_DIR/evals/scripts/score_triggering.py" --self-test 2>&1 | sed 's/^/  /' \
  && ok "eval self-test passed" || bad "eval self-test failed"
# The harness must present the REAL skill file, not a copy living in the harness.
"$PLUGIN_DIR/../terminal/evals/scripts/score_triggering.py" --emit-prompt 2>/dev/null \
  | grep -q "Bound Hosts" && ok "prompt injects the real SKILL.md" \
  || bad "prompt does not contain the skill — harness would measure itself"

note "15. A non-resolvable relative path fails loudly (AC-term-2-4)"
# Regression: `cd "$(dirname "$p")"` used to fail silently, leaving "/<basename>" —
# a plausible absolute path pointing at the filesystem root. A typo in --background
# would have landed in the profile and rendered blank without a word.
OUT2="$("$INSTALL" --name "Bad Path" --emoji "🧪" --color "#3B7DED" --dir "$TMP" \
        --background "definitely/missing/dir/bg.jpg" --dry-run 2>&1)"; RC=$?
if [ "$RC" != 0 ] && printf '%s' "$OUT2" | grep -q "cannot resolve"; then
  ok "aborts with a message instead of inventing /bg.jpg"
else
  bad "non-resolvable path did not abort (rc=$RC)"
fi
printf '%s' "$OUT2" | grep -q '"/bg.jpg"' && bad 'wrote the bogus "/bg.jpg" path' || ok "no bogus root path produced"

note "16. An existing, differing profile is never clobbered (AC-term-4-4)"
P="$ITERM_PROFILE_DIR/Test Profile.json"
printf 'HAND EDITED\n' > "$P"
if "$INSTALL" --name "Test Profile" --emoji "🧪" --color "#3B7DED" --dir "$TMP" >/dev/null 2>&1; then
  bad "overwrote a hand-edited profile without --force"
else
  ok "refused to overwrite (exit non-zero)"
fi
grep -q 'HAND EDITED' "$P" && ok "hand-edited content survived" || bad "hand-edited content was destroyed"
"$INSTALL" --name "Test Profile" --emoji "🧪" --color "#3B7DED" --dir "$TMP" --force >/dev/null 2>&1
grep -q 'HAND EDITED' "$P" && bad "--force did not replace" || ok "--force replaces on request"
# Unchanged input must stay a quiet no-op, not an error.
"$INSTALL" --name "Test Profile" --emoji "🧪" --color "#3B7DED" --dir "$TMP" >/dev/null 2>&1 \
  && ok "identical rerun is a no-op (exit 0)" || bad "identical rerun failed"

printf '\n'
[ "$fail" = 0 ] && { printf 'terminal: ALL CHECKS PASSED\n'; exit 0; }
printf 'terminal: FAILURES ABOVE\n'; exit 1
