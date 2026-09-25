#!/usr/bin/env bash
# Struktur-Konvention prüfen (SPEC-repo-conventions §3, US-conv-1).
# config-valid-Tier: rein statisch, offline, zero-dep. Exit != 0 bei Verstoß.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 2
fail=0
note() { printf '  ✗ %s\n' "$1"; fail=1; }
ok()   { printf '  ✓ %s\n' "$1"; }

echo "[structure] AC-1-1: Top-Level-Ordner vorhanden"
for d in plugins specs docs journal plans tests; do
  if [ -d "$d" ]; then ok "$d/"; else note "Top-Level-Ordner fehlt: $d/"; fi
done

echo "[structure] AC-1-2: keine specs/ unterhalb von docs/"
while IFS= read -r p; do note "specs/ unter docs/: $p"; done < <(find . -type d -path '*/docs/*specs*' -not -path '*/node_modules/*' 2>/dev/null)
find . -type d -path '*/docs/*specs*' -not -path '*/node_modules/*' 2>/dev/null | grep -q . || ok "keine specs unter docs"

echo "[structure] AC-1-4: Spec-Dateien am Namen als product/tech erkennbar"
while IFS= read -r sp; do
  base="$(basename "$sp")"
  case "$base" in
    README.md) ;;
    *_product_*|*_tech_*) ok "erkennbar: $sp" ;;
    *) note "Spec ohne _product_/_tech_-Token: $sp" ;;
  esac
done < <(find specs -name '*.md' 2>/dev/null)

echo "[structure] US-conv-1: Plugin-Ordner bleiben rein (kein specs/docs/journal/plans drin)"
# Plugin-Ordner = Top-Level-Dir mit .claude-plugin/
for pj in plugins/*/.claude-plugin/plugin.json; do
  [ -e "$pj" ] || continue
  plug="${pj%%/.claude-plugin/plugin.json}"
  for meta in specs docs journal plans; do
    if [ -d "$plug/$meta" ]; then note "Plugin '$plug' enthält $meta/ (gehört auf Top-Level)"; fi
  done
done
[ "$fail" -eq 0 ] && ok "alle Plugin-Ordner rein"

echo "[structure] US-conv-5: jede description ≤ 1024 Zeichen, Frontmatter striktes YAML"
# Die Copilot CLI verweigert ein Plugin ganz, sobald eine description das Limit
# reißt — Claude Code lädt es trotzdem, der Fehler ist dort unsichtbar. Geprüft
# werden marketplace.json, plugin.json, Skills, Agents und Commands.
while IFS= read -r line; do
  case "$line" in
    "OK Negativ"*) ok "${line#OK }" ;;
    OK*)   ok "alle ${line#OK } descriptions im Limit" ;;
    FAIL*) note "${line#FAIL }" ;;
  esac
done < <(python3 "$ROOT/tests/lib/check_descriptions.py" --self-test; python3 "$ROOT/tests/lib/check_descriptions.py" "$ROOT")

echo "[structure] US-conv-4: Marketplace-Manifest deckt sich mit den Plugins"
# Gilt fuer JEDES Plugin: registriert, source loest auf, Version identisch zu
# plugin.json. Die Implementierung liegt zentral in tests/lib/, damit die
# plugin-lokalen Suites dieselbe Pruefung aufrufen statt sie zu kopieren.
bash "$ROOT/tests/lib/check-version-sync.sh"
rc=$?
case "$rc" in
  0) ;;
  2) note "Versions-Check nicht ausfuehrbar (kein JSON-Parser) — gilt als Verstoss" ;;
  *) fail=1 ;;
esac

if [ "$fail" -eq 0 ]; then echo "[structure] PASS"; else echo "[structure] FAIL"; fi
exit "$fail"
