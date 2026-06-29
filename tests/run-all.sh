#!/usr/bin/env bash
# Aggregator für alle Plugin-/Repo-Test-Suites (SPEC-repo-conventions §5).
# Offline, zero-dep. Ruft jede Suite, sammelt Fehlschläge, Exit != 0 wenn eine rot.
#
# AUTO-DISCOVERY: jede `tests/<plugin>/run.sh` wird automatisch eingehängt — so
# kann eine Plugin-Migration ihre Suite andocken, ohne diese Datei zu ändern
# (keine Merge-Konflikte auf dem Aggregator bei parallelen Plugin-PRs).
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
rc=0
run() { printf '\n=== %s ===\n' "$1"; shift; "$@" || rc=1; }

# Repo-Struktur (config-valid) — immer zuerst.
run "structure" bash "$ROOT/structure/check.sh"

# Plugin-Suiten: tests/<plugin>/run.sh, alphabetisch.
for s in "$ROOT"/*/run.sh; do
  [ -e "$s" ] || continue
  name="$(basename "$(dirname "$s")")"
  run "$name" bash "$s"
done

printf '\n=== run-all: %s ===\n' "$([ $rc -eq 0 ] && echo PASS || echo FAIL)"
exit "$rc"
