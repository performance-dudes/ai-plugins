#!/usr/bin/env bash
# Wrapper: hängt die code-nahe Suite ocr/tests/validate.sh in den Aggregator ein
# (SPEC-repo-conventions §5, „einteilig"). Der Test bleibt beim Plugin; dieser
# Wrapper ruft ihn nur, damit tests/run-all.sh ihn per Auto-Discovery findet.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/../../ocr/tests/validate.sh"
