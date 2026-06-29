#!/usr/bin/env bash
# Spec-Touch-Gate (SPEC-repo-conventions §4/§7): ein PR, der PRODUKT-Dateien ändert
# (Plugin-Runtime/Code), muss auch ein PROZESS-Artefakt berühren (specs/ ODER docs/
# ODER journal/). Sonst rot — „kein Code-PR ohne Spec/Docs/Journal".
#
# Bypass mit Begründung: trägt irgendeine Commit-Message im Bereich auf einer
# EIGENEN ZEILE (Trailer-Stil) den Marker
#   [skip-conventions: <grund>]
# läuft das Gate grün durch (die Begründung steht damit dauerhaft in der History).
# Eigene Zeile bewusst: sonst matcht schon eine Doku, die den Marker bloß ERWÄHNT.
#
# Vergleichsbasis: $BASE_REF (CI setzt das auf den PR-Base), sonst origin/main.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT" || exit 2
BASE="${BASE_REF:-origin/main}"
RANGE_BASE="$(git merge-base "$BASE" HEAD 2>/dev/null || echo "$BASE")"

changed="$(git diff --name-only "$RANGE_BASE"...HEAD 2>/dev/null)"
[ -z "$changed" ] && { echo "[spec-touch] keine Änderungen ggü. $BASE — ok"; exit 0; }

# PROZESS-Artefakte berührt?
process="$(printf '%s\n' "$changed" | grep -E '^(specs|docs|journal)/' || true)"

# PRODUKT-Dateien berührt? = irgendeine Datei in einem Plugin-Ordner (Top-Level-Dir
# mit .claude-plugin/), aber NICHT die Prozess-Ordner. README-only zählt nicht.
plugins="$(for pj in plugins/*/.claude-plugin/plugin.json; do [ -e "$pj" ] && printf '%s\n' "${pj%%/.claude-plugin/plugin.json}"; done)"
product=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in */README.md) continue;; esac        # reine README-Änderung ist kein Produkt-Touch
  for p in $plugins; do
    case "$f" in "$p"/*) product="$product$f"$'\n';; esac
  done
done <<< "$changed"

if [ -z "$product" ]; then
  echo "[spec-touch] keine Produkt-Dateien geändert — Gate nicht einschlägig, ok"; exit 0
fi

# Bypass-Marker in einer Commit-Message des Bereichs?
if git log --format='%B' "$RANGE_BASE"..HEAD 2>/dev/null | grep -qE '^[[:space:]]*\[skip-conventions:[^]]+\][[:space:]]*$'; then
  echo "[spec-touch] Bypass-Marker [skip-conventions: …] (eigene Zeile) gefunden — Gate übersprungen (Begründung in History)"; exit 0
fi

if [ -n "$process" ]; then
  echo "[spec-touch] Produkt- UND Prozess-Artefakte berührt — ok"; exit 0
fi

echo "[spec-touch] FAIL: Produkt-Dateien geändert, aber kein specs/docs/journal berührt:"
printf '%s' "$product" | sed 's/^/    /'
echo "  → Spec/Docs/Journal ergänzen, ODER eine Commit-Message mit [skip-conventions: <grund>] versehen."
exit 1
