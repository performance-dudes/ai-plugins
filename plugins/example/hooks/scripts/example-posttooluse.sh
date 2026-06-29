#!/usr/bin/env bash
# Example PostToolUse hook. Receives the hook event as JSON on stdin.
# Unlike PreToolUse (which fires BEFORE a tool runs and can block it), PostToolUse
# fires AFTER the tool has executed — so the stdin JSON also carries the result
# (tool_name, tool_input, and tool_response). It cannot un-run the call; it is for
# observing, logging, or adding follow-up context.
# Exit 0 = continue. Print JSON to stdout to add context (see docs).
# This example is a harmless no-op that just logs to stderr.
set -euo pipefail

input="$(cat)"
echo "[example plugin] PostToolUse hook saw a Bash call complete" >&2

# Nothing to do — let the session continue.
exit 0
