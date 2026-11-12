# Doc: `mechanic` plugin (agents `mechanic` + `errand`)

The `mechanic` plugin ships two cost-tiered subagents, each on a cheaper model
family so the premium tier stays free for judgment.

## The two agents

| Agent | `subagent_type` | Model | Tier | For |
|---|---|---|---|---|
| `mechanic` | `mechanic` | `sonnet` | mid | mechanical work needing code/context comprehension |
| `errand` | `mechanic:errand` | `haiku` | cheapest | trivial self-contained transformations, no codebase understanding |

Both have broad tool access but are behaviourally constrained and instructed to hand
back the moment a task belongs to a neighbouring tier or the instruction is ambiguous.

## Selecting a tier — the routing rule

```
Needs a DECISION            -> general-purpose  (premium)
Needs CODE/CONTEXT to do    -> mechanic         (Sonnet)
TRIVIAL transformation      -> errand           (Haiku)
```

- **errand** — classify/label, extract a field, reformat (JSON/CSV/whitespace/case),
  literal find/replace with exact old→new, yes/no checks, count, sort, normalize.
- **mechanic** — apply a specified edit that must fit its surroundings, refactor across
  files, boilerplate that must slot into a codebase, run a known command and interpret.
- **general-purpose** — design, debugging an unknown cause, review, prose, open-ended
  relevance-weighted search.

Mnemonic: needs a decision → premium; needs code understanding → mechanic; otherwise →
errand.

## The `SessionStart` hook — putting the rule in the context

Claude Code loads only an agent's frontmatter `description:` into the model. The
routing rule itself — the cascade above, the `inline` route, the round-up asymmetry,
the parallelism rules — lives in this doc and the README, and **neither is ever
loaded**. Without the hook the orchestrator sees two tools but not the rule for
choosing between them (and never learns that a lone trivial item shouldn't be
delegated at all).

| File | Role |
|---|---|
| `hooks/routing-card.md` | the card — **single source** of the injected text |
| `hooks/sessionstart-routing.sh` | emits the card verbatim as `additionalContext` |
| `hooks/hooks.json` | registers the hook on `SessionStart` |

```
SessionStart (startup · resume · clear · compact)
   └─ sessionstart-routing.sh
        └─ {"hookSpecificOutput":{"hookEventName":"SessionStart",
                                  "additionalContext": <routing-card.md verbatim>}}
```

Design decisions, each load-bearing:

- **`SessionStart`, not `UserPromptSubmit`** — the block is paid once per session
  segment instead of every turn, and `SessionStart` also fires on `compact`, so the
  rule survives the compaction that would otherwise drop it first.
- **Injected, never duplicated** — the script `cat`s the card; it holds no copy of the
  text. `tests/mechanic/run.sh` asserts `additionalContext` is byte-identical to
  `routing-card.md`, so the two cannot drift. (Repo doctrine: test the real object.)
- **Under 1400 characters (AC-4-8)** — the card sits in every user's context window,
  so its length is a permanent tax. It carries only what is *not* already there: the
  two agent descriptions already cover "what is trivial" and "when to hand back". The
  card's reason to exist is the `inline` route, the round-up rule, and parallelism.
  Prose and rationale belong here in the docs, not in the card. Over budget → shorten
  the card, don't raise the budget.
- **Zero-dep, fail-open** — pure bash (no `jq`/`python`/`node`, since a hook that
  can't run fails silently). A missing or unreadable card exits 0 with no output; a
  session must never break because of it.
- **No enforcement** — it injects context only. No `PreToolUse` veto, no rewriting of
  agent calls. The caller still decides; it just decides informed.

## Model aliases — how they resolve

| Path | Result |
|------|--------|
| Agent frontmatter `model:` | `sonnet` / `haiku` → the current model of that family. |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` / `ANTHROPIC_DEFAULT_HAIKU_MODEL` | override the alias target per machine — gateways such as Foundry set them to their own IDs. |

The frontmatter carries an alias, never a full model ID: a full ID goes stale with every
model release and breaks on gateways that name models differently. Who needs a fixed
version sets the environment variable, not the plugin.

Source: [Claude Code subagents documentation](https://code.claude.com/docs/en/sub-agents.md),
section "Choose a model".

## Operational note

The agent registry is read at **session start** and is not hot-reloaded. After
installing or updating the plugin, start a **fresh session**. Verify with a one-line
spawn that returns each agent's model ID (a Sonnet / a Haiku model).

## Model comparison

| | Haiku (`errand`) | Sonnet (`mechanic`) | Opus (`general-purpose`) |
|---|---|---|---|
| In/Out per 1M (prices as of the 5.5 generation) | $0.10 / $0.50 | $2 / $10 | $4 / $20 |
| Context / max out | 1M / 128K | 1M / 128K | 1M / 128K |
| `effort` param | yes (default `medium`) | yes (default `high`) | yes (default `medium`) |
