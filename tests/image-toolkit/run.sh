#!/usr/bin/env bash
# Wrapper: hängt die code-nahe Suite image-toolkit/tests/validate.sh in den
# Aggregator ein (SPEC-repo-conventions §5, „einteilig"). Der Test bleibt beim
# Plugin; dieser Wrapper ruft ihn nur, damit tests/run-all.sh ihn per
# Auto-Discovery findet.
#
# Fehlte bis 2026-07-25: validate.yml fuhr plugins/*/tests/validate.sh und sah
# die Suite, run-all.sh nicht — derselbe Fehlermodus (CI prüft, lokal nicht),
# der den Versions-Drift drei Wochen unentdeckt ließ.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/../../plugins/image-toolkit/tests/validate.sh"
