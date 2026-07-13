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

## The other rule — test the REAL object, inject it, NEVER a copy

Just as load-bearing as "don't tune the cases": **the eval must run against the
real object under test** — the actual `SKILL.md`, the actual agent frontmatter, the
actual command/workflow file, invoked exactly as it ships. Never against a
paraphrase, a summary, or a hand-kept copy of it pasted into your test harness.

Why this is a hard rule, not a nicety:

- A copy **drifts**. The moment the real skill description changes and your pasted
  copy doesn't, the eval measures *the copy* — a green run then proves nothing about
  the plugin. You have built a test that tests itself.
- A copy **leaks**. When you re-type the object into a prompt you unconsciously
  smooth it, add examples that happen to mirror your cases, or drop the awkward
  clause that was the whole point — and the number comes back beautiful and
  meaningless.

So **inject, don't duplicate**: the harness READS the real file at run time.
- Structured/routing: drive the *installed* plugin headlessly (`claude -p "…"`) or
  read the real agent/skill file and feed its verbatim content — the routes come
  from the shipping object, not a description of it. (`mechanic/evals/routing/
  build_router_prompt.py` shows the pattern: it reads the real `agents/*.md`
  frontmatter at build time, so changing the plugin automatically changes the test.)
- Free-text: `judge.py` calls the **real greeter** with its production system
  prompt — not a retyped "pretend you are a greeter."

If you ever catch yourself pasting a skill/agent description into an eval file,
stop: reference the real file instead. A test of a copy is not a test of the plugin.

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
   the measuring stick, not the judge. A case is lock-ready only when **two domain
   experts would reach the same pass/fail** on it — if they wouldn't, the expectation
   is still fuzzy; sharpen it, don't freeze it (Anthropic's clarity bar).
2. **Run the real plugin — no mock.** Capture what actually ships. And test the
   **real object**, injected not copied (see the rule above).
3. **Grade the output, not the tool-call path.** Assert on the observable outcome
   (which entrypoint fired, the greeting produced) — never on an exact multi-step
   trajectory. Path-grading is rigid and over-fits (Anthropic).
4. **Always include clean / precision cases.** Without them the specificity /
   false-positive axis is invisible.
5. **Grade difficulty** (easy → hard) so you see *where* the plugin gets timid.
6. **Run N trials, report pass^k / mean±σ.** One trial is an anecdote. Anthropic
   treats non-determinism as first-class: **pass@k** (≥1 of k succeeds) for
   exploration, **pass^k** (all k succeed) as the bar when a suite is allowed to call
   itself green for customer-facing reliability.
7. **Start from real failures, feed the loop.** Anthropic's advice is to seed a suite
   with **20–50 simple tasks drawn from real failures**, not pretty synthetic ones. A
   confirmed false trigger → a new locked `clean` case; a real miss → a new seeded
   case. Then fix the plugin and re-measure.

## The vocabulary (Anthropic's terms, so we speak the standard)

Anthropic's "Demystifying evals for AI agents" names the parts; this harness maps to
them one-to-one, so use these words:

| Anthropic term | here |
|---|---|
| **evaluation suite** | a sub-folder (`routing/`, `greeting/`) |
| **task** | one locked case (a prompt + its expectation) |
| **trial** | one run of a case (repeat N for pass^k) |
| **grader** | `score_routing.py` (deterministic) / `judge.py` (LLM) |
| **transcript** | the captured output (`predictions.*.yaml`, the judged response) |
| **outcome** | PASS / FAIL |
| **evaluation harness** | the scripts + cases |
| **agent harness / scaffold** | the REAL plugin under test (`claude -p`, the real agent) |

## Sources

First-hand Anthropic method (the canonical grounding):
- [Demystifying evals for AI agents — Anthropic (9 Jan 2026)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — the vocabulary above, pass@k/pass^k, "tasks from real failures", grade-output-not-path, deterministic-first graders.
- [Define success criteria and build evaluations — Claude Docs](https://docs.claude.com/en/docs/test-and-evaluate/develop-tests) — the grader hierarchy (code-based → LLM-based → human).
- [Anthropic courses — Prompt evaluations](https://raw.githubusercontent.com/anthropics/courses/master/prompt_evaluations/README.md) — the official prompt-eval workflow.

There is **no first-party plugin-eval framework** (not even in preview): officially
`plugin validate` (hygiene) + headless `claude -p` + your own assertions. The one
first-party eval tool is `skill-creator` (skills only). This harness fills that gap.
- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) — the built-in `skill-creator` skill-eval loop (skills only).
- [cc-plugin-eval — plugin component-triggering eval (YAML config, programmatic-first + LLM judge)](https://github.com/sjnims/cc-plugin-eval)
- [skill-eval-action — grade skills against YAML cases (`expect_skill`, ≥1 negative)](https://github.com/skill-bench/skill-eval-action)
- [Measuring Claude Code skill activation with sandboxed evals — Scott Spence](https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals)
- [Test-case configuration (YAML as native format) — promptfoo](https://www.promptfoo.dev/docs/configuration/test-cases/)
- Deeper generic harness: `plugin-eval@ai-plugins-internal` (confusion-matrix scorer, Cohen's κ, mean±σ).
