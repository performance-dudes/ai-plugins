# evals — measure the plugin like a test, not a vibe

The other components show what a plugin *is*. This one shows how you tell whether
it actually **works**: a small, real, runnable eval harness. It is the rigorous,
scored version of `tests/README.md` §3 ("does the model pick this skill?") — the
same question, but with locked ground truth, a confusion matrix, and a pass/fail.

Copy this folder into your own plugin and swap the cases. For the full,
domain-generic harness (findings-style scorer, Cohen's κ judge validation,
mean±σ aggregation), reach for **`plugin-eval@ai-plugins-internal`** — this is the
lean, self-contained teaching copy.

## The one rule — read this first

> **The eval tests the PLUGIN. You fix the PLUGIN, never the cases.**

Once a case is locked and correctly encodes the expectation, it is frozen. A
failing case is a signal about the **skill description, the agent prompt, or the
workflow** — go fix *those*. You do **not** relax a case, delete it, or reword the
expectation to make a run go green. That is overfitting the test to the code, and
it destroys the only thing an eval is for: an honest, stable measuring stick.

Corollary — **diversity beats a green number.** Cases vary language (en/de),
phrasing (explicit / implicit / slash-command / paraphrase), and near-miss family
on purpose. A suite that only tests `"greet X"` ten ways proves nothing; one that
also throws meta-questions, keyword collisions, and adversarial coding prompts at
the router measures whether the plugin *understood the intent*.

## The one decision rule — pick the regime per suite

```
        Is the expected output STRUCTURED or FREE-TEXT / semantic?
                   │                                   │
            STRUCTURED                          FREE-TEXT / fuzzy
     (which entrypoint fires: a label)   (the greeting wording: tone, name, language)
                   │                                   │
        DETERMINISTIC matching                   LLM-as-a-JUDGE
        → scripts/score_routing.py               → scripts/judge.py
   cheap · reproducible · zero variance      two-call · forced tool_use · temp 0
```

Reach for a judge **only** when correctness is genuinely semantic. If a matcher
can decide it, match it — it is cheaper, reproducible, and has zero judge-variance.
This is exactly the split Claude Code's own plugin-eval tooling makes
(`detection_mode: programmatic_first`, then LLM judgment).

## Layout — one sub-folder per eval suite

Past a single case list, split by *what you are measuring*:

```
evals/
  routing/                       # STRUCTURED regime — component triggering
    ground_truth.yaml            #   locked, human-curated, diverse cases
    predictions.example.yaml     #   a captured real run (so scoring needs no model)
  greeting/                      # FREE-TEXT regime — the produced greeting
    cases.yaml                   #   locked expectations (IS / IS NOT, safety)
  scripts/
    score_routing.py             # deterministic scorer (confusion matrix)
    judge.py                     # LLM-as-a-judge (the two-call pattern)
  README.md
```

## Why YAML, not JSON

The cases are **human-authored and locked**, and the per-case `note` / `description`
IS the calibration anchor. YAML keeps that anchor an inline comment right next to
the case, and diffs stay readable when a case changes — which is why Claude Code's
plugin-eval frameworks configure in YAML (`config.yaml`) and promptfoo treats YAML
as its native test-case format. Machine-scale datasets still use JSONL; a small,
curated, argued-over suite like this wants YAML. (Both scripts read either —
`yaml.safe_load` parses JSON too.)

## Suite 1 — routing (structured, deterministic)

`routing/ground_truth.yaml` locks 10 diverse prompts, each with the route that
SHOULD fire: `greet` (the run-greet skill / `/greet`) or `none` (stay silent).
Four are `clean: true` near-misses — a meta-question about the code, a keyword
collision, an unrelated ask, an adversarial coding prompt — that MUST route to
`none`. Those are the **specificity axis**: they catch a skill whose `description`
is so greedy it fires on anything mentioning "greet".

Run it:

```bash
# 1. capture a REAL run of the plugin (no mock) — one route per case.
#    Drive each prompt headlessly and classify what fired, e.g.:
claude -p "say hi to the Performance Dudes" --output-format json | jq -r '.result'
#    Record the routes into predictions.yaml (see predictions.example.yaml for shape).
#    Triggering is stochastic — capture N samples per case and take the majority
#    (report pass@k / mean±σ, never trust a single run).

# 2. score the capture against the locked ground truth (deterministic, no model):
uv run evals/scripts/score_routing.py \
  --truth evals/routing/ground_truth.yaml \
  --pred  evals/routing/predictions.example.yaml
```

You get a per-route confusion matrix, precision / recall / F1, and a specificity
line. A mismatch is printed as a **plugin bug to fix** — with a `[clean/near-miss
→ false trigger]` tag when the skill over-fired. Exit code is non-zero on any miss
so it can gate CI.

## Suite 2 — greeting (free-text, LLM-as-a-judge)

`greeting/cases.yaml` locks what a *good greeting* is — addresses the person by
name, one warm line, replies in the asked language — plus a zero-tolerance safety
case (an injection that tries to extract the system prompt). The judge runs the
**two-call pattern**: call the real greeter (production system prompt, temp ≈ 0.3),
then a temperature-0 judge with **forced `tool_use`** that checks the response
against the human expectation *only*. Parsing is defensive — a garbled judge field
defaults to failing, so a bad judge response never silently passes.

```bash
export ANTHROPIC_API_KEY=…            # never hard-code; the judge needs it
uv run evals/scripts/judge.py --cases evals/greeting/cases.yaml
```

Same rule: if `warm_not_robotic` fails, you improve the greeter agent — you do not
delete the check.

## The discipline (both suites)

1. **Lock the expectation before the run.** The human-written note/description is
   the measuring stick, not the judge.
2. **Run the real plugin — no mock.** Capture what actually ships.
3. **Always include clean / precision cases.** Without them the specificity /
   false-positive axis is invisible.
4. **Grade difficulty** (easy → hard) so you see *where* the plugin gets timid.
5. **Run N times, report mean±σ / pass@k.** One run is an anecdote.
6. **Feed the loop.** A confirmed false trigger → a new locked `clean` case; a miss
   → a new seeded case. Then fix the plugin and re-measure.

## Sources

- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
- [cc-plugin-eval — 4-stage plugin component-triggering eval (YAML config, programmatic-first + LLM judge)](https://github.com/sjnims/cc-plugin-eval)
- [Measuring Claude Code skill activation with sandboxed evals — Scott Spence](https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals)
- [Demystifying evals for AI agents — Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Test-case configuration (YAML as native format) — promptfoo](https://www.promptfoo.dev/docs/configuration/test-cases/)
- Deeper generic harness: `plugin-eval@ai-plugins-internal` (confusion-matrix scorer, Cohen's κ, mean±σ).
