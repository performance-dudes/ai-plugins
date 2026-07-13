# mechanic evals — measure the routing, never tune the test

The `mechanic` plugin promises **one thing**: a sharp routing decision. For any
task it should pick the right tier — do it **inline**, or delegate to **errand**
(Haiku 4.5), **mechanic** (Sonnet 4.6), or **general-purpose** (premium). Everything
else (the model pins, the tool access) only matters if that decision is right. So
this is what the eval measures.

## The one rule — read this first

> **The eval tests the PLUGIN. A miss is fixed at the plugin (the errand/mechanic
> agent descriptions, the routing rule in the README) — the cases are NEVER
> changed.**

Once a case here correctly encodes the expectation it is **frozen**. A run that
misroutes it is a **plugin bug**: the description didn't make the boundary clear
enough. You fix the description and re-run — you do **not** reword or delete the case
to make the number go green. That would overfit the test to the code and destroy the
only reason the eval exists. (This is the same rule the `example` plugin's evals
spell out, and the method behind it is `plugin-eval@ai-plugins-internal`.)

## What routes where — four outcomes, two axes

```
                    does the task need a DECISION?
                     (design · debug unknown · review · naming · prose)
                          │ yes
                          ▼
                   general-purpose (premium)
                          │ no
        does it need to UNDERSTAND CODE/CONTEXT to execute a decided change?
                          │ yes → mechanic (Sonnet 4.6)
                          │ no  → it's trivial. now the SECOND axis:
                          ▼
              is there VOLUME (a batch, a whole file/dataset, a long scan)?
                     yes → errand (Haiku 4.5)      no → INLINE (do it yourself)
```

Two independent axes, not one ladder:

- **Capability** (the *under-routing* axis): `errand < mechanic < {inline,
  general-purpose}`. Sending a task to a model too weak → it fails → retry at
  premium. This is the dangerous error.
- **Delegation economics** (`inline` vs `errand`): a lone trivial task inline (zero
  overhead) vs a batch offloaded to Haiku (cheap tokens × volume). Getting this wrong
  is *wasteful*, not dangerous — but it's the most common real mistake ("spawn a
  subagent for one tiny thing").

## Why an `inline` route at all

The subtle bug this eval guards against: treating **every** trivial task as "send it
to the cheap agent." Delegation isn't free — an agent run burns roughly **4× the
tokens** of a plain orchestrator turn (spawn + context transfer + result
reintegration; Anthropic's multi-agent report). For a *single* small item that fixed
overhead outweighs the cheap-model saving, so **inline wins**. `errand` only pays off
once a **batch** amortises the overhead. The `i0*` (inline) and `e0*` (errand) cases
are the same trivial ops at single vs batch scale — that pair is the whole point.

## Prefer one tier too expensive over one too cheap

The routing error is **asymmetric**, and the scorer treats it that way:

- **Over-route** (too expensive) — the task still succeeds; you just overpaid a little.
- **Under-route** (too cheap) — the tier isn't up to it, fails, and you pay the failed
  cheap attempt **plus** the retry at the right tier. Cascades pay *cheap + strong*,
  never just strong; and cheap/strong model errors correlate, so the query the cheap
  model flubs is disproportionately a hard one.

So `score_routing.py` reports an **under-routing rate** as a first-class metric next
to F1, and its cost model charges a **retry penalty** whenever a run under-routes on
capability — quantifying exactly why "round up when in doubt" is the right rule.

## Layout

```
evals/
├── README.md                       ← you are here
├── routing/
│   ├── ground_truth.yaml           ← 20 locked, diverse cases (4 routes × 5)
│   └── predictions.example.yaml    ← a captured routing run, scored by CI
└── scripts/
    └── score_routing.py            ← deterministic scorer (F1 + under-routing + cost)
```

YAML, not JSON: the cases are human-authored and locked, and each `note`/`trap` is a
calibration anchor that lives best as an inline comment next to the case. (YAML is the
case/config form Claude Code's own plugin-eval tooling uses.)

## Run it

```bash
# score the committed sample (what CI runs — must exit 0)
uv run evals/scripts/score_routing.py

# score a fresh run you captured
uv run evals/scripts/score_routing.py --pred path/to/predictions.yaml --json
```

The scorer prints accuracy, per-route precision/recall/F1, the under-routing rate,
and the cost model (baseline all-premium → ideal routed → effective routed with retry
penalty). Exit 0 = every case routed as its locked expectation; exit 1 = at least one
miss (a plugin bug to fix here).

## How a real run is produced — inject the real object, never a copy

The "prediction" for a case is a routing decision: given only the plugin's agent
descriptions and a task prompt, which tier fires? That is exactly what a real
orchestrator with `mechanic` installed does.

**The golden rule: test the REAL object.** The router must see the *actual*
`agents/errand.md` / `agents/mechanic.md` descriptions — the exact string a live
registry serves — not a paraphrase re-typed into the harness. A copy drifts from the
plugin the moment either changes, and then the eval measures the copy, not the
plugin. (This is a real failure mode: an early run of this very eval leaked because
the harness pasted hand-written route examples that mirrored the cases — the number
came back a meaningless 20/20.)

So `routing/build_router_prompt.py` **injects** the real object: it reads the
verbatim frontmatter `description:` from `agents/*.md` and the task prompts from
`ground_truth.yaml` at build time, strips every answer field, and swaps the
route-hinting case ids (`i01…`, `g04…`) for neutral `t01…` ids in a deterministic,
RNG-free shuffle (so the 4×5 balance and the prefixes can't leak). Change a
description in the plugin and the next build tests the changed plugin — no drift.

```bash
# 1. build the BLIND prompt from the real plugin (writes routing/.idmap.json)
uv run evals/routing/build_router_prompt.py > /tmp/router_prompt.md

# 2. feed /tmp/router_prompt.md to N fresh agents (blind); save each JSON array

# 3. translate a captured run back to case ids, then score
uv run evals/routing/build_router_prompt.py --translate run1.json > /tmp/pred.yaml
uv run evals/scripts/score_routing.py --pred /tmp/pred.yaml
```

Run N fresh agents — each is a *trial* — and take the majority (routing is
stochastic; one trial is an anecdote). Report **pass^k** (all k trials agree with the
locked outcome) as the bar, not a single run. A miss tells you which boundary in the
descriptions is still fuzzy — fix it *there*, re-run, and only then re-capture
`predictions.example.yaml`.

**Result on the committed plugin:** three blind trials through this harness were
unanimous and matched the locked ground truth on every case — i.e. **pass^3 = 1.0**,
accuracy 1.000, macro-F1 1.000, under-routing 0.000, cost model ~79% saved vs
all-premium. Two honest caveats: (1) a clean 20/20 means the suite hasn't yet found
the plugin's breaking point — the next useful move is to keep adding harder
near-misses until one misroutes (that miss is the plugin's real weak spot, and the
reason to fix a description); (2) these 20 cases are hand-designed near-misses, not
yet harvested from **real failures** — Anthropic's advice is to seed 20–50 tasks from
actual misroutes, so every real production misroute should become a new locked case.

## Grounded in Anthropic's method — the vocabulary

Anthropic's "Demystifying evals for AI agents" names the parts; this suite maps to
them one-to-one:

| Anthropic term | here |
|---|---|
| **evaluation suite** | `routing/` |
| **task** | one locked case in `ground_truth.yaml` |
| **trial** | one blind router run (repeat N for pass^k) |
| **grader** | `score_routing.py` (deterministic — routing is a label) |
| **transcript** | the captured routes (`predictions.example.yaml`) |
| **outcome** | PASS / FAIL |
| **evaluation harness** | `build_router_prompt.py` + `score_routing.py` + the cases |
| **agent harness / scaffold** | the REAL plugin — the injected `agents/*.md` |

Two of their rules shape this suite directly: a task must be so unambiguous that
**two experts would grade it the same** (that's the lock bar), and you **grade the
outcome, not the tool-call path** — here we grade the route *decision* (a label), the
observable output of the orchestrator's classification, never an enforced trajectory.

## Sources

- Canonical method (first-hand): Anthropic, "[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)"
  (task/trial/grader/suite vocabulary, pass^k, tasks-from-real-failures,
  grade-output-not-path) and "[Define success criteria and build evaluations](https://docs.claude.com/en/docs/test-and-evaluate/develop-tests)"
  (deterministic → LLM → human grader hierarchy). No first-party plugin-eval framework
  exists (not even in preview); this fills that gap.
- The method as a plugin: `plugin-eval@ai-plugins-internal` (write → **measure** →
  optimize; structured → deterministic, free-text → LLM-judge) and the runnable minimal
  example at `plugins/example/evals/` in this repo.
- Routing/cascade grounding: FrugalGPT (arXiv 2305.05176), RouteLLM (2406.18665),
  cost-saving cascades with early abstention (2502.09054), "Is Escalation Worth It?"
  (2605.06350) — the asymmetric-cost and % cost-saved-at-iso-quality framing.
- Delegation overhead: Anthropic, "How we built our multi-agent research system"
  (~4× tokens for agents, ~15× for multi-agent; delegate only when value/volume pays).
