#!/usr/bin/env bash
# mechanic — config-valid-Tier (SPEC-mechanic §5). Rein statisch, offline, zero-dep.
# Prüft AC-1-1, AC-1-2, AC-1-5, AC-2-1 (config-valid) sowie AC-4-1..AC-4-6, AC-4-8
# (config-valid + script-run + hook-behavior). Exit != 0 bei Verstoß.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLUG="$ROOT/plugins/mechanic"
fail=0
note() { printf '  ✗ %s\n' "$1"; fail=1; }
ok()   { printf '  ✓ %s\n' "$1"; }

# JSON-Validierung: python3 (stdlib) falls vorhanden, sonst node --check-Ersatz via node -e.
json_valid() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$1" 2>/dev/null
  elif command -v node >/dev/null 2>&1; then
    node -e 'JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"))' "$1" 2>/dev/null
  else
    return 0  # kein Parser verfügbar → JSON-Parse überspringen (grep-Checks greifen weiter)
  fi
}

echo "[mechanic] AC-1-1: plugin.json valide, name=mechanic"
PJ="$PLUG/.claude-plugin/plugin.json"
if [ -f "$PJ" ]; then
  json_valid "$PJ" && ok "plugin.json ist valides JSON" || note "plugin.json ist kein valides JSON"
  grep -q '"name"[[:space:]]*:[[:space:]]*"mechanic"' "$PJ" && ok 'name: "mechanic"' || note 'name != "mechanic"'
else note "plugin.json fehlt"; fi

echo "[mechanic] AC-1-2: agent-Frontmatter (name + model-Pin)"
AG="$PLUG/agents/mechanic.md"
if [ -f "$AG" ]; then
  # Frontmatter-Block extrahieren (zwischen erstem und zweitem '---')
  fm="$(awk 'NR==1&&/^---/{f=1;next} f&&/^---/{exit} f{print}' "$AG")"
  printf '%s\n' "$fm" | grep -qE '^name:[[:space:]]*mechanic[[:space:]]*$' \
    && ok "name: mechanic" || note "Frontmatter name != mechanic"
  printf '%s\n' "$fm" | grep -qE '^model:[[:space:]]*claude-sonnet-4-6[[:space:]]*$' \
    && ok "model: claude-sonnet-4-6 (Versions-Pin)" || note "model-Pin != claude-sonnet-4-6"
else note "agents/mechanic.md fehlt"; fi

echo "[mechanic] AC-1-5: errand-Frontmatter (name + Haiku-Pin)"
ER="$PLUG/agents/errand.md"
if [ -f "$ER" ]; then
  efm="$(awk 'NR==1&&/^---/{f=1;next} f&&/^---/{exit} f{print}' "$ER")"
  printf '%s\n' "$efm" | grep -qE '^name:[[:space:]]*errand[[:space:]]*$' \
    && ok "name: errand" || note "Frontmatter name != errand"
  printf '%s\n' "$efm" | grep -qE '^model:[[:space:]]*claude-haiku-4-5[[:space:]]*$' \
    && ok "model: claude-haiku-4-5 (Versions-Pin)" || note "model-Pin != claude-haiku-4-5"
else note "agents/errand.md fehlt"; fi

echo "[mechanic] AC-2-1: Marketplace-Eintrag"
MP="$ROOT/.claude-plugin/marketplace.json"
if [ -f "$MP" ]; then
  json_valid "$MP" && ok "marketplace.json ist valides JSON" || note "marketplace.json ist kein valides JSON"
  grep -q '"source"[[:space:]]*:[[:space:]]*"\./plugins/mechanic"' "$MP" \
    && ok 'source: "./plugins/mechanic"' || note "mechanic nicht in marketplace.json registriert"
else note "marketplace.json fehlt"; fi

echo "[mechanic] AC-4-1: hooks.json registriert den SessionStart-Hook"
HJ="$PLUG/hooks/hooks.json"
HS="$PLUG/hooks/sessionstart-routing.sh"
CARD="$PLUG/hooks/routing-card.md"
if [ -f "$HJ" ]; then
  json_valid "$HJ" && ok "hooks.json ist valides JSON" || note "hooks.json ist kein valides JSON"
  grep -q '"SessionStart"' "$HJ" && ok "SessionStart-Event registriert" || note "kein SessionStart in hooks.json"
  grep -q 'CLAUDE_PLUGIN_ROOT' "$HJ" \
    && ok "Pfad über \${CLAUDE_PLUGIN_ROOT} (portabel)" || note "hartkodierter Pfad statt \${CLAUDE_PLUGIN_ROOT}"
  grep -q 'sessionstart-routing.sh' "$HJ" && ok "ruft sessionstart-routing.sh" || note "Hook-Script nicht referenziert"
else note "hooks/hooks.json fehlt"; fi

echo "[mechanic] AC-4-6: Hook ist zero-dep und syntaktisch sauber"
if [ -f "$HS" ]; then
  bash -n "$HS" 2>/dev/null && ok "bash -n sauber" || note "Syntaxfehler in sessionstart-routing.sh"
  # Zero-dep: keine Abhängigkeit auf jq/python/node im Ausführungspfad (Kommentare ausgenommen).
  if grep -vE '^[[:space:]]*#' "$HS" | grep -qE '\b(jq|python3?|node)\b'; then
    note "Hook ruft jq/python/node auf — muss zero-dep bleiben"
  else ok "keine externen Tools (jq/python/node)"; fi
else note "hooks/sessionstart-routing.sh fehlt"; fi

echo "[mechanic] AC-4-4 / AC-4-8: Routing-Karte inhaltlich + im Context-Budget"
if [ -f "$CARD" ]; then
  for token in 'general-purpose' 'mechanic:errand' 'INLINE'; do
    grep -q -- "$token" "$CARD" && ok "Route genannt: $token" || note "Route fehlt in der Karte: $token"
  done
  grep -qi 'higher one\|round up\|under-rout' "$CARD" \
    && ok "Round-up-/Asymmetrie-Regel vorhanden" || note "Asymmetrie-Regel fehlt in der Karte"
  grep -qi 'parallel' "$CARD" && ok "Parallelisierungs-Abschnitt vorhanden" || note "Parallelisierung fehlt in der Karte"
  grep -qi 'disjoint' "$CARD" \
    && ok "Disjunktheits-Bedingung für schreibende Fan-outs" || note "Disjunktheits-Regel fehlt"
  # AC-4-8: harte Obergrenze — die Karte liegt in JEDEM Session-Abschnitt im Context.
  bytes="$(wc -c < "$CARD" | tr -d ' ')"
  if [ "$bytes" -lt 1400 ]; then ok "Karte im Budget: ${bytes} < 1400 Zeichen"
  else note "Karte über Budget: ${bytes} >= 1400 Zeichen — kürzen, nicht Budget erhöhen"; fi
else note "hooks/routing-card.md fehlt"; fi

echo "[mechanic] AC-4-2 / AC-4-3 / AC-4-5: Hook-Verhalten (real ausgeführt)"
if [ -f "$HS" ] && [ -f "$CARD" ]; then
  out="$(printf '{"session_id":"test","source":"startup"}' \
        | CLAUDE_PLUGIN_ROOT="$PLUG" bash "$HS" 2>/dev/null)"
  if [ -n "$out" ]; then
    ok "Hook liefert Ausgabe"
    # AC-4-2 + AC-4-3: JSON valide, richtiges Event, additionalContext == Karte (byte-identisch).
    if command -v python3 >/dev/null 2>&1; then
      CARD="$CARD" python3 -c '
import json,os,sys
d = json.loads(sys.stdin.read())
h = d["hookSpecificOutput"]
assert h["hookEventName"] == "SessionStart", "hookEventName != SessionStart"
ctx = h["additionalContext"]
assert ctx.strip(), "additionalContext ist leer"
card = open(os.environ["CARD"], encoding="utf-8").read()
assert ctx == card.rstrip("\n"), "additionalContext weicht von routing-card.md ab (Drift!)"
' <<<"$out" 2>/dev/null \
        && ok "valides JSON, SessionStart, Context == routing-card.md (kein Drift)" \
        || note "Hook-Ausgabe ungültig oder von der Karte abgedriftet"
    else
      printf '%s' "$out" | grep -q '"hookEventName":"SessionStart"' \
        && ok "SessionStart-Ausgabe (grep-Fallback, kein python3)" || note "hookEventName fehlt"
    fi
  else note "Hook liefert keine Ausgabe"; fi

  # AC-4-5: fehlende Karte darf die Session nie brechen.
  tmp="$(mktemp -d)"; mkdir -p "$tmp/hooks"; cp "$HS" "$tmp/hooks/"
  miss="$(printf '{"source":"startup"}' | CLAUDE_PLUGIN_ROOT="$tmp" bash "$tmp/hooks/sessionstart-routing.sh" 2>/dev/null)"
  rc=$?
  [ "$rc" -eq 0 ] && [ -z "$miss" ] \
    && ok "fehlende Karte: Exit 0, leere Ausgabe (Session bleibt intakt)" \
    || note "fehlende Karte bricht den Hook (rc=$rc, out='${miss}')"
  rm -rf "$tmp"
fi

if [ "$fail" -eq 0 ]; then echo "[mechanic] PASS"; else echo "[mechanic] FAIL"; fi
exit "$fail"
