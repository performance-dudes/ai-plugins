#!/usr/bin/env bash
# Example PreToolUse hook. Receives the hook event as JSON on stdin.
# Exit 0 = allow. Print JSON to stdout to add context or block (see docs).
# This example is a harmless no-op that just logs to stderr and allows the call.
set -euo pipefail

input="$(cat)"
echo "[example plugin] PreToolUse hook saw a Bash call" >&2

# Allow the tool call to proceed.
exit 0
