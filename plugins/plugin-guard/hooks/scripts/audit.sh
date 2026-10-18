#!/usr/bin/env bash
# plugin-guard — SessionStart-Hook: startet den Start-Audit (scan.py).
# Ohne python3 wird nur gemeldet, nie blockiert; das Mod-Gate bleibt davon unberührt.
# Immer Exit 0: SessionStart kann nichts blockieren, ein Audit-Fehler darf die Session
# nicht stören. Nur Bash-Builtins bis zum python3-Aufruf (kein dirname/cat nötig).
HERE="${BASH_SOURCE[0]%/*}"
if ! command -v python3 >/dev/null 2>&1; then
  printf '{"systemMessage":"plugin-guard: python3 fehlt — Start-Audit übersprungen (Mod-Gate aktiv)."}\n'
  exit 0
fi
python3 "$HERE/scan.py" --hook || true
exit 0
