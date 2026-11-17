# tests/token-guard

Spec: [`specs/token-guard/0001_product_token-guard.md`](../../specs/token-guard/0001_product_token-guard.md).
Traceability: [`coverage.md`](coverage.md).

## Product type and placement

One-part plugin (hooks plus one command, no build step). So all tests live here at
top level (`SPEC-repo-conventions` §5); the offload eval lives in the plugin under
`plugins/token-guard/evals/`, like `mechanic`.

## Run

```bash
bash tests/token-guard/run.sh      # offline, node ≥ 18; eval step needs uv
bash tests/run-all.sh              # picks this suite up automatically
bash tests/token-guard/e2e.sh      # manual: real `claude -p` session, needs login
```

## What runs

| File | Type | Covers |
|---|---|---|
| `run.sh` §config-valid | config-valid | JSON manifests parse, `node --check` on every module, `claude plugin validate` when available |
| `guard.test.mjs` | script-run | pure logic: classification, streaks, verify reset, outside detection, env parsing, budgets |
| `hooks.test.mjs` | hook-behavior | the **real command string from `hooks.json`** per event, in a temporary `HOME` |
| `metrics.test.mjs` | script-run | metrics schema, parallel writers, stats script, transcript reader, latency |
| `parity.test.mjs` | script-run | copy vs. built opencode original on `fixtures/parity.json`; deliberate deviations asserted to still differ |
| `run.sh` §eval | eval | `plugins/token-guard/evals/` offload detector, pass^3 |
| `e2e.sh` | e2e | headless session with the plugin from the working tree; third single Bash call refused, metrics record it |

Hook tests use a temporary `HOME`, so they never touch your real `~/.claude`. On macOS
the temp dir is under `/var/folders` (allowlisted), so "outside" test paths use
`/srv/…`; the hook only inspects the command text and never runs it.
