# Spec: Hooks component

**Theme:** The plugin ships a safe, isolated-testable example hook that demonstrates
the event → program → exit-code mechanism.

## US-HOOKS-1 — A safe, testable example hook

> As a **plugin author**, I want a safe hook example I can test in isolation, so
> that I can learn how hooks work without risk.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-HOOKS-1-1 | The hook script exists at `example/hooks/scripts/example-pretooluse.sh`. | `test.sh` (file presence) |
| AC-HOOKS-1-2 | Run in isolation with a sample event, it exits `0` (allow). | `test.sh` (pipe JSON, check exit) |
| AC-HOOKS-1-3 | The hooks config `hooks.json.example` is valid JSON. | `test.sh` (`python3 -m json.tool`) |
