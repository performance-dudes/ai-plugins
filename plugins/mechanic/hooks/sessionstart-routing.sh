#!/usr/bin/env bash
# mechanic — SessionStart hook (SPEC-mechanic §4, US-mech-4).
#
# Claude Code loads only the agents' frontmatter `description:` into the model's
# context. The routing rule itself — the cascade, the inline route, the
# round-up-when-in-doubt asymmetry, the parallelism rules — lives in the README,
# which is never loaded. This hook injects it as SessionStart additionalContext so
# the orchestrator has the rule, not just the two tools.
#
# Injects the REAL object: it emits hooks/routing-card.md verbatim, so the card is
# the single source and the hook cannot drift from it (repo CLAUDE.md, eval doctrine).
#
# Zero-dep by design: pure bash, no jq/python/node. A hook that cannot run is a
# silent failure, so it must not depend on anything beyond the shell.
set -u

CARD="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}/hooks/routing-card.md"

# Drain stdin (the hook payload); we inject on every source — startup, resume,
# clear and especially compact, where the context was just rewritten.
cat >/dev/null 2>&1 || true

# Missing card must never break a session: emit nothing, exit clean.
[ -r "$CARD" ] || exit 0

card="$(cat "$CARD")" || exit 0
[ -n "$card" ] || exit 0

# Escape as a JSON string: backslash first, then quote, then control chars.
card="${card//\\/\\\\}"
card="${card//\"/\\\"}"
card="${card//$'\t'/\\t}"
card="${card//$'\r'/\\r}"
card="${card//$'\n'/\\n}"

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$card"
