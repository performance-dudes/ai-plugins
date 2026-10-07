#!/usr/bin/env bash
# event-trace — klassischer Command-Hook, auf JEDES Hook-Event registriert
# (hooks/hooks.json). Liest das Event-JSON von stdin und hängt eine Zeile an
#   $EVENT_TRACE_DIR/<session_id>.hooks.jsonl   (Default: ~/.claude/event-trace)
#
# Reiner Beobachter: schreibt NICHTS auf stdout (bei SessionStart/UserPromptSubmit
# würde stdout als Kontext beim Modell landen) und endet immer mit Exit 0
# (Exit 2 würde blockieren). Ein Fehler beim Loggen darf die Session nie stören.
set -u

event="${1:-unknown}"
input="$(cat 2>/dev/null || true)"

dir="${EVENT_TRACE_DIR:-${HOME:-/tmp}/.claude/event-trace}"
mkdir -p "$dir" 2>/dev/null || exit 0

# session_id ohne jq-Abhängigkeit herausziehen; Fallback "no-session".
sid="$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
sid="$(printf '%s' "${sid:-no-session}" | tr -c 'A-Za-z0-9._-' '_')"

# JSON-Strings enthalten keine rohen Zeilenumbrüche — Newlines entfernen ergibt
# gültiges Ein-Zeilen-JSON. Leerer/ungültiger Input wird als null geloggt.
payload="$(printf '%s' "$input" | tr -d '\r\n')"
case "$payload" in
  \{*\}) ;;
  *) payload=null ;;
esac

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"  # Sekunden genügen; BSD-date (macOS) kennt kein %N
printf '{"ts":"%s","layer":"hook","event":"%s","pid":%s,"input":%s}\n' \
  "$ts" "$event" "$$" "$payload" >>"$dir/$sid.hooks.jsonl" 2>/dev/null

exit 0
