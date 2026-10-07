#!/usr/bin/env bash
# Smoke test for the event-trace plugin.
# Run from anywhere:  bash plugins/event-trace/tests/validate.sh
# Traceability: SPEC-event-trace AC-et-*, see tests/event-trace/coverage.md
set -uo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$PLUGIN_DIR/hooks/scripts/log-hook.sh"
HOOKS="$PLUGIN_DIR/hooks/hooks.json"
fail=0

note() { printf '\n=== %s ===\n' "$1"; }
ok()   { printf '  ✔ %s\n' "$1"; }
bad()  { printf '  x %s\n' "$1"; fail=1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

note "1. Component files present"
for f in .claude-plugin/plugin.json README.md hooks/hooks.json hooks/register.ts \
         hooks/scripts/log-hook.sh tests/trace.test.ts; do
  [ -f "$PLUGIN_DIR/$f" ] && ok "$f" || bad "missing $f"
done
[ -x "$SCRIPT" ] && ok "log-hook.sh is executable" || bad "log-hook.sh not executable"

note "2. Static validity (config-valid)"
for j in .claude-plugin/plugin.json hooks/hooks.json; do
  python3 -m json.tool "$PLUGIN_DIR/$j" >/dev/null 2>&1 && ok "$j is valid JSON" || bad "$j invalid JSON"
done
bash -n "$SCRIPT" && ok "log-hook.sh syntax" || bad "log-hook.sh syntax"

note "3. Every hook event registered (AC-et-1-1, AC-et-1-3)"
# The hook events of Claude Code 2.1.x minus WorktreeCreate/WorktreeRemove (a command
# hook there REPLACES git worktree handling and must print a path — see spec).
EXPECTED="SessionStart Setup InstructionsLoaded UserPromptSubmit UserPromptExpansion
PreToolUse PermissionRequest PermissionDenied PostToolUse PostToolUseFailure PostToolBatch
Notification MessageDisplay Elicitation ElicitationResult SubagentStart SubagentStop
TaskCreated TaskCompleted TeammateIdle PreCompact PostCompact PreModelSwitch PostModelSwitch
ConfigChange CwdChanged DirectoryAdded FileChanged Stop StopFailure SessionEnd"
python3 - "$HOOKS" $EXPECTED <<'PY' && ok "31 events, each → log-hook.sh <Event>, no worktree hooks" || bad "hooks.json event coverage"
import json, sys
doc = json.load(open(sys.argv[1])); expected = set(sys.argv[2:])
hooks = doc.get("hooks", {})
errors = []
if set(hooks) != expected:
    errors.append(f"missing={sorted(expected - set(hooks))} extra={sorted(set(hooks) - expected)}")
for event, groups in hooks.items():
    cmds = [h.get("command", "") for g in groups for h in g.get("hooks", [])]
    if len(cmds) != 1 or not cmds[0].endswith(f"log-hook.sh\" {event}"):
        errors.append(f"{event}: {cmds}")
if {"WorktreeCreate", "WorktreeRemove"} & set(hooks):
    errors.append("worktree hook registered")
if errors: print("\n".join(errors), file=sys.stderr)
sys.exit(1 if errors else 0)
PY

note "4. Mod module wired (AC-et-2-1)"
python3 -c "import json,sys; sys.exit(0 if json.load(open('$HOOKS')).get('modules')==['./register.ts'] else 1)" \
  && ok "hooks.json modules → ./register.ts" || bad "modules entry"
grep -q "on('\*'," "$PLUGIN_DIR/hooks/register.ts" && ok "register.ts hooks on(\"*\")" || bad "no on(\"*\") hook"
grep -q "on('telemetry.\*', { to: 'collector' }" "$PLUGIN_DIR/hooks/register.ts" \
  && ok "register.ts hooks telemetry.* (collector)" || bad "no telemetry hook"

note "5. log-hook.sh behaviour (script-run, AC-et-1-2, AC-et-1-4)"
export EVENT_TRACE_DIR="$TMP/logs"
out="$(printf '{\n  "session_id": "abc-123",\n  "hook_event_name": "Stop",\n  "x": "a b"\n}\n' | bash "$SCRIPT" Stop)"; rc=$?
[ $rc -eq 0 ] && ok "exit 0" || bad "exit $rc"
[ -z "$out" ] && ok "no stdout" || bad "stdout not empty: $out"
log="$EVENT_TRACE_DIR/abc-123.hooks.jsonl"
if [ -f "$log" ] && python3 - "$log" <<'PY'
import json, sys
lines = open(sys.argv[1]).read().splitlines()
assert len(lines) == 1, lines
d = json.loads(lines[0])
assert d["layer"] == "hook" and d["event"] == "Stop", d
assert d["input"]["session_id"] == "abc-123" and d["input"]["x"] == "a b", d
PY
then ok "one valid JSONL line with layer/event/input"; else bad "log line wrong or missing"; fi

printf '{"session_id":"abc-123"}' | bash "$SCRIPT" PreToolUse >/dev/null
[ "$(wc -l <"$log")" -eq 2 ] && ok "appends (2nd line)" || bad "not appended"

out="$(printf 'not json' | bash "$SCRIPT" Notification)"; rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok "garbage input → exit 0, silent" || bad "garbage input rc=$rc out=$out"
grep -q '"event":"Notification","pid":[0-9]*,"input":null' "$EVENT_TRACE_DIR/no-session.hooks.jsonl" 2>/dev/null \
  && ok "garbage input logged as null under no-session" || bad "garbage input not logged as null"

touch "$TMP/blocker"
out="$(EVENT_TRACE_DIR="$TMP/blocker/sub" bash "$SCRIPT" Stop </dev/null 2>&1)"; rc=$?
[ $rc -eq 0 ] && [ -z "$out" ] && ok "unwritable log dir → exit 0, silent" || bad "unwritable dir rc=$rc out=$out"

note "6. Engine checks (claude plugin validate / test)"
if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$PLUGIN_DIR" >"$TMP/validate.txt" 2>&1 && ok "claude plugin validate" \
    || { bad "claude plugin validate"; cat "$TMP/validate.txt"; }
  claude plugin test "$PLUGIN_DIR" >"$TMP/test.txt" 2>&1 && ok "claude plugin test ($(grep -o '[0-9]* pass' "$TMP/test.txt"))" \
    || { bad "claude plugin test"; cat "$TMP/test.txt"; }
else
  printf '  - claude CLI not found — skipping validate/test (mod tests need the engine)\n'
fi

printf '\n=== event-trace: %s ===\n' "$([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
