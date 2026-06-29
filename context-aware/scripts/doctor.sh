#!/usr/bin/env bash
# Preflight check for the context-aware plugin.
# Prints one line per dependency: OK / MISS (needs a fix) / ---- (optional).
# Installs nothing — only reports. Run from anywhere:
#   bash context-aware/scripts/doctor.sh
set -uo pipefail

ok()   { printf '  OK   %s\n' "$1"; }
miss() { printf '  MISS %s  — %s\n' "$1" "$2"; }
opt()  { printf '  ---- %s  (%s)\n' "$1" "$2"; }

printf '\n=== context-aware preflight ===\n\n'
printf 'required\n'

# claude CLI — needed for the agent passes
if command -v claude >/dev/null 2>&1; then
  ok "claude CLI"
else
  miss "claude CLI" "install Claude Code — the agent passes need it"
fi

# node >= 20 — the Workflow tool runtime
if command -v node >/dev/null 2>&1; then
  ver="$(node --version 2>/dev/null | sed 's/^v//')"
  major="${ver%%.*}"
  if [ "${major:-0}" -ge 20 ] 2>/dev/null; then
    ok "node $ver (>= 20)"
  else
    miss "node $ver" "Workflow tool needs node >= 20 — 'brew install node' (Bash fallback works without)"
  fi
else
  miss "node" "Workflow tool needs node >= 20 — 'brew install node' (Bash fallback works without)"
fi

# context-mode plugin — the ctx_* retrieval substrate this plugin relies on.
# It is enabled once at the workspace level, NOT bundled per plugin.
if command -v claude >/dev/null 2>&1 && claude plugin list 2>/dev/null | grep -qi 'context-mode'; then
  ok "context-mode plugin (ctx_* retrieval substrate)"
else
  miss "context-mode plugin" "enable it once at the workspace level: 'claude plugin marketplace add mksglu/context-mode' then 'claude plugin install context-mode@context-mode' — without it the ctx_* tools are absent and the agents fall back to reading reference files directly"
fi

printf '\nVerdict: ready when claude, node and the context-mode plugin are OK.\n\n'
