# token-guard evals — measure the detector, never tune the test

Most of token-guard is deterministic rules with a single right answer per input;
those are covered by tests (`tests/token-guard/`). The one part whose *quality* is
open-ended is the **offload-ask detector** (`isOffloadAsk` in `hooks/lib/guard.mjs`):
does it recognise when the assistant hands project work to the user, without
flagging the assistant describing its own work? That is what this suite measures.

## The one rule

> **The eval tests the PLUGIN. A miss is fixed in the detector — the cases are NEVER
> changed.**

## Suite

| Suite | Regime | Cases | Grader |
|---|---|---|---|
| `offload/` | structured (boolean) | `offload/ground_truth.yaml` — 24 locked cases, de/en, families explicit · implicit · outside · near-miss | `scripts/score_offload.py`, deterministic matcher |

The scorer imports the **real** detector via node (injected, not copied), runs k
trials and reports **pass^k**, precision, recall and per-family results. It exits 0
only at pass^k = 100 %.

```bash
uv run plugins/token-guard/evals/scripts/score_offload.py 3
```

`tests/token-guard/run.sh` runs it when `uv` is available.

## Results

| Date | Detector | pass^3 | Precision | Recall |
|---|---|---|---|---|
| 2026-11-17 | opencode original (first run, cases locked) | 18/24 = 75 % | 0.83 | 0.71 |
| 2026-11-17 | token-guard 0.1.0 | 24/24 = 100 % | 1.00 | 1.00 |

The cases were written before the first run, without real-failure transcripts. Every
confirmed miss from a real session becomes a new locked case.
