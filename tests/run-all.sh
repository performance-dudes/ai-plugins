#!/usr/bin/env bash
# Tests the WHOLE example plugin: every config valid, every script runnable.
# Run from anywhere:  bash tests/run-all.sh
# Does NOT activate the defused .example components — it only validates them.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EX="$ROOT/example"
fail=0
ok()  { printf '  ok   %s\n' "$1"; }
bad() { printf '  x    %s\n' "$1"; fail=1; }

echo "== JSON & .example (must be valid JSON) =="
while IFS= read -r f; do
  python3 -m json.tool "$f" >/dev/null 2>&1 && ok "${f#$ROOT/}" || bad "${f#$ROOT/} (invalid JSON)"
done < <(find "$EX" -type f \( -name '*.json' -o -name '*.json.example' \) | sort)

echo "== JavaScript (workflow) =="
while IFS= read -r f; do
  node --check "$f" 2>/dev/null && ok "${f#$ROOT/}" || bad "${f#$ROOT/} (JS syntax error)"
done < <(find "$EX" -type f -name '*.js' | sort)

echo "== Shell scripts (syntax + executable) =="
while IFS= read -r f; do
  bash -n "$f" 2>/dev/null || { bad "${f#$ROOT/} (syntax)"; continue; }
  [ -x "$f" ] && ok "${f#$ROOT/} (+x)" || bad "${f#$ROOT/} (not executable)"
done < <(find "$EX" -type f -name '*.sh' | sort)

echo "== Hook runs in isolation (exit 0 = allow) =="
if echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' \
   | bash "$EX/hooks/scripts/example-pretooluse.sh" >/dev/null 2>&1; then
  ok "PreToolUse hook exits 0"
else
  bad "PreToolUse hook did not exit 0"
fi

echo "== PD structure present =="
for d in specs docs journal tests; do
  [ -d "$ROOT/$d" ] && ok "$d/ exists" || bad "$d/ missing"
done

echo
[ "$fail" -eq 0 ] && echo "  ALL CHECKS PASSED" || echo "  FAILURES ABOVE"
exit "$fail"
