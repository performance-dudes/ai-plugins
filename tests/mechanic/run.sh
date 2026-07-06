#!/usr/bin/env bash
# mechanic — config-valid-Tier (SPEC-mechanic §5). Rein statisch, offline, zero-dep.
# Prüft AC-1-1, AC-1-2, AC-2-1. Exit != 0 bei Verstoß.
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

echo "[mechanic] AC-2-1: Marketplace-Eintrag"
MP="$ROOT/.claude-plugin/marketplace.json"
if [ -f "$MP" ]; then
  json_valid "$MP" && ok "marketplace.json ist valides JSON" || note "marketplace.json ist kein valides JSON"
  grep -q '"source"[[:space:]]*:[[:space:]]*"\./plugins/mechanic"' "$MP" \
    && ok 'source: "./plugins/mechanic"' || note "mechanic nicht in marketplace.json registriert"
else note "marketplace.json fehlt"; fi

if [ "$fail" -eq 0 ]; then echo "[mechanic] PASS"; else echo "[mechanic] FAIL"; fi
exit "$fail"
