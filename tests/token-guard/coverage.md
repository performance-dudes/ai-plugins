# Coverage — token-guard

Drei Achsen (SPEC-repo-conventions §6). Spec: `specs/token-guard/0001_product_token-guard.md`.
Typen: `config-valid` · `script-run` · `hook-behavior` · `e2e`, dazu die Eval-Suite.
Code-Pfade relativ zu `plugins/token-guard/`.

## spec : code

| AC | Code |
|---|---|
| AC-tg-1-1, 1-3 | `hooks/lib/guard.mjs` (`classifyBash`, `onBashBefore`) |
| AC-tg-1-2, 1-4 | `hooks/lib/handler.mjs` (`PreToolUse`), `hooks/hooks.json` |
| AC-tg-1-5, 7-3 | `hooks/lib/store.mjs` (`updateSession`, `deleteSession`) |
| AC-tg-2-1..2-3 | `hooks/lib/guard.mjs` (`onEdit`, `onVerifyAfter`), `hooks/lib/handler.mjs` |
| AC-tg-3-1, 3-2, 3-5 | `hooks/lib/transcript.mjs` |
| AC-tg-3-3, 3-4 | `hooks/lib/guard.mjs` (`checkStepBudget`, `checkContextBudget`), `hooks/lib/handler.mjs` (`PostToolUse`, `Stop`, `UserPromptSubmit`) |
| AC-tg-4-1 | `hooks/lib/guard.mjs` (`mutatesOutsideProject`) |
| AC-tg-4-2, 4-3 | `hooks/lib/handler.mjs` (`PreToolUse`) |
| AC-tg-5-1, 5-2 | `hooks/lib/guard.mjs` (`isOffloadAsk`), `hooks/lib/handler.mjs` (`Stop`) |
| AC-tg-5-3 | `evals/offload/ground_truth.yaml`, `evals/scripts/score_offload.py` |
| AC-tg-6-1, 6-2 | `hooks/lib/store.mjs` (`bumpMetrics`, `withLock`) |
| AC-tg-6-3 | `hooks/stats.mjs`, `commands/token-guard.md` |
| AC-tg-7-1 | `hooks/lib/guard.mjs` (`optionsFromEnv`) |
| AC-tg-7-2 | `hooks/token-guard.mjs` (catch-all, exit 0), `hooks/hooks.json` (`command -v node`), `hooks/lib/store.mjs` (`validSessionId`, corrupt state) |
| AC-tg-7-4 | `hooks/lib/transcript.mjs` (incremental read) |
| AC-tg-7-5 | `hooks/lib/guard.mjs` vs. `../opencode/opencode-token-guard/dist/guard.js` |
| AC-tg-7-6 | `.claude-plugin/plugin.json`, `../../.claude-plugin/marketplace.json` |
| AC-tg-8-1 | ganzes Plugin |

## spec : test (pro Typ)

| AC | config-valid | script-run | hook-behavior | eval | e2e |
|---|---|---|---|---|---|
| AC-tg-1-1 | — | `guard.test` | — | — | — |
| AC-tg-1-2 | — | — | `hooks.test` | — | `e2e.sh` |
| AC-tg-1-3 | — | `guard.test` | — | — | `e2e.sh` (Zähler nach Block neu) |
| AC-tg-1-4, 1-5 | — | — | `hooks.test` | — | — |
| AC-tg-2-1, 2-2 | — | — | `hooks.test` | — | — |
| AC-tg-2-3 | — | `guard.test` | — | — | — |
| AC-tg-3-1, 3-2, 3-5 | — | `metrics.test` | — | — | — |
| AC-tg-3-3 | — | `guard.test` | `hooks.test` | — | — |
| AC-tg-3-4 | — | — | `hooks.test` | — | — |
| AC-tg-4-1 | — | `guard.test`, `parity.test` | — | — | — |
| AC-tg-4-2, 4-3 | — | — | `hooks.test` | — | — |
| AC-tg-5-1 | — | `parity.test` | `hooks.test` | — | — |
| AC-tg-5-2 | — | — | `hooks.test` | — | — |
| AC-tg-5-3 | — | — | — | `score_offload.py` | — |
| AC-tg-6-1..6-3 | — | `metrics.test` | — | — | `e2e.sh` (Metrik-Datei) |
| AC-tg-7-1 | — | `guard.test` | — | — | — |
| AC-tg-7-2, 7-3 | — | — | `hooks.test` | — | `e2e.sh` (Session-Datei gelöscht) |
| AC-tg-7-4 | — | `metrics.test` | — | — | — |
| AC-tg-7-5 | — | `parity.test` | — | — | — |
| AC-tg-7-6 | `run.sh`, `tests/structure/check.sh` | — | — | — | — |
| AC-tg-8-1 | — | — | — | — | `e2e.sh` (manuell, nicht in CI) |

## code : tests

| Komponente | config-valid | script-run | hook-behavior | eval | e2e |
|---|---|---|---|---|---|
| `hooks/hooks.json` | `run.sh` | — | `hooks.test` (echter Befehl) | — | `e2e.sh` |
| `hooks/token-guard.mjs` | `node --check` | — | `hooks.test` | — | `e2e.sh` |
| `hooks/lib/handler.mjs` | `node --check` | — | `hooks.test` | — | `e2e.sh` |
| `hooks/lib/guard.mjs` | `node --check` | `guard.test`, `parity.test` | `hooks.test` | `score_offload.py` | `e2e.sh` |
| `hooks/lib/store.mjs` | `node --check` | `metrics.test` | `hooks.test` | — | `e2e.sh` |
| `hooks/lib/transcript.mjs` | `node --check` | `metrics.test` | `hooks.test` | — | — |
| `hooks/stats.mjs` | `node --check` | `metrics.test` | — | — | — |
| `commands/token-guard.md` | `claude plugin validate` | — | — | — | manuell 2026-11-17: `claude -p "/token-guard:token-guard" --plugin-dir …` gibt die Statistik aus |

## Lücken

- `/token-guard:token-guard` ist nur manuell geprüft (2026-11-17), nicht automatisiert.
- AC-tg-8-1 läuft nur manuell (Login nötig); Ergebnis im Journal.
