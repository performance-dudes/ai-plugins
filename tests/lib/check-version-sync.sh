#!/usr/bin/env bash
# Marketplace-Manifest gegen die Plugins auf Platte prüfen
# (SPEC-repo-conventions US-conv-4; SPEC-mechanic AC-2-3).
#
# Die Version eines Plugins steht an ZWEI Orten: im Eintrag in
# .claude-plugin/marketplace.json und in plugins/<name>/.claude-plugin/plugin.json.
# Driften sie, zieht ein Nutzer beim `marketplace update` eine andere Version als
# die, gegen die getestet wurde — die Suite grün, die Auslieferung falsch.
#
# Genau das ist real passiert und blieb drei Wochen unentdeckt (validate.yml war
# vom 2026-07-06 bis 2026-07-25 rot, acht Runs in Folge). Deshalb liegt der Check
# hier zentral statt in einer Plugin-Suite: er gilt für JEDES Plugin, und beide
# Ebenen (repo-weit + plugin-lokal) rufen dieselbe Implementierung auf, damit die
# Prüfungen nicht auseinanderlaufen.
#
# Aufruf:
#   check-version-sync.sh          -> alle Plugins
#   check-version-sync.sh mechanic -> nur dieses Plugin
#
# Exit 0 = konsistent, 1 = Drift/Lücke, 2 = nicht prüfbar (kein JSON-Parser).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ONLY="${1:-}"

# Zero-dep-Prinzip wie im Rest der Suite: python3 bevorzugt, node als Ersatz.
# Fehlt beides, wird NICHT still durchgewunken, sondern mit Exit 2 gemeldet —
# ein ungeprüfter Check, der grün aussieht, ist schlimmer als ein lauter.
if command -v python3 >/dev/null 2>&1; then
  RUNNER=(python3 -)
elif command -v node >/dev/null 2>&1; then
  echo "  ! kein python3 — Versions-Check übersprungen (node-Pfad nicht implementiert)" >&2
  exit 2
else
  echo "  ! weder python3 noch node — Versions-Check nicht ausführbar" >&2
  exit 2
fi

"${RUNNER[@]}" "$ROOT" "$ONLY" <<'PY'
import json, pathlib, sys

root = pathlib.Path(sys.argv[1])
only = sys.argv[2] if len(sys.argv) > 2 else ""
fail = 0

def note(m):
    global fail
    print(f"  ✗ {m}")
    fail = 1

def ok(m):
    print(f"  ✓ {m}")

mp_path = root / ".claude-plugin" / "marketplace.json"
if not mp_path.is_file():
    note("marketplace.json fehlt")
    raise SystemExit(1)

try:
    entries = json.loads(mp_path.read_text()).get("plugins", [])
except json.JSONDecodeError as e:
    note(f"marketplace.json ist kein valides JSON: {e}")
    raise SystemExit(1)

registered = {e.get("name"): e for e in entries}

# AC-4-1: kein Plugin auf Platte, das im Marketplace fehlt. Ein unregistriertes
# Plugin wird nie ausgeliefert — es existiert nur fuer den, der das Repo klont.
if not only:
    on_disk = {p.parent.parent.name for p in root.glob("plugins/*/.claude-plugin/plugin.json")}
    for name in sorted(on_disk - set(registered)):
        note(f"{name}: liegt in plugins/, fehlt aber in marketplace.json")
    if not on_disk - set(registered):
        ok(f"alle {len(on_disk)} Plugins auf Platte sind registriert")

targets = [only] if only else sorted(registered)
if only and only not in registered:
    note(f"{only}: kein Eintrag in marketplace.json")
    raise SystemExit(1)

for name in targets:
    entry = registered[name]
    src = entry.get("source", "")
    pj = root / src.lstrip("./") / ".claude-plugin" / "plugin.json"
    # AC-4-3: source muss aufloesen, sonst zeigt der Marketplace ins Leere.
    if not pj.is_file():
        note(f"{name}: source '{src}' loest nicht auf ({pj} fehlt)")
        continue
    try:
        pj_ver = json.loads(pj.read_text()).get("version")
    except json.JSONDecodeError as e:
        note(f"{name}: plugin.json ist kein valides JSON: {e}")
        continue
    mp_ver = entry.get("version")
    # AC-4-2: beide Versionen muessen gesetzt UND gleich sein.
    if not mp_ver:
        note(f"{name}: marketplace.json-Eintrag hat kein 'version'-Feld")
    elif not pj_ver:
        note(f"{name}: plugin.json hat kein 'version'-Feld")
    elif mp_ver != pj_ver:
        note(f"{name}: Versions-Drift — marketplace {mp_ver} != plugin.json {pj_ver}")
    else:
        ok(f"{name} ({pj_ver}) konsistent")

raise SystemExit(fail)
PY
