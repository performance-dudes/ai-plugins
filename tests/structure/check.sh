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
for d in specs docs journal plans tests; do
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
for pj in */.claude-plugin/plugin.json; do
  [ -e "$pj" ] || continue
  plug="${pj%%/.claude-plugin/plugin.json}"
  for meta in specs docs journal plans; do
    if [ -d "$plug/$meta" ]; then note "Plugin '$plug' enthält $meta/ (gehört auf Top-Level)"; fi
  done
done
[ "$fail" -eq 0 ] && ok "alle Plugin-Ordner rein"

if [ "$fail" -eq 0 ]; then echo "[structure] PASS"; else echo "[structure] FAIL"; fi
exit "$fail"
