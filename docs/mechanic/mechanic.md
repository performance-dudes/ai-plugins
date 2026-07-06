# Doc: `mechanic` plugin (agents `mechanic` + `errand`)

The `mechanic` plugin ships two cost-tiered subagents, each pinned to a cheaper model
version so the premium tier stays free for judgment.

## The two agents

| Agent | `subagent_type` | Model pin | Tier | For |
|---|---|---|---|---|
| `mechanic` | `mechanic` | `claude-sonnet-4-6` | mid | mechanical work needing code/context comprehension |
| `errand` | `mechanic:errand` | `claude-haiku-4-5` | cheapest | trivial self-contained transformations, no codebase understanding |

Both have broad tool access but are behaviourally constrained and instructed to hand
back the moment a task belongs to a neighbouring tier or the instruction is ambiguous.

## Selecting a tier — the routing rule

```
Needs a DECISION            -> general-purpose  (premium)
Needs CODE/CONTEXT to do    -> mechanic         (Sonnet 4.6)
TRIVIAL transformation      -> errand           (Haiku 4.5)
```

- **errand** — classify/label, extract a field, reformat (JSON/CSV/whitespace/case),
  literal find/replace with exact old→new, yes/no checks, count, sort, normalize.
- **mechanic** — apply a specified edit that must fit its surroundings, refactor across
  files, boilerplate that must slot into a codebase, run a known command and interpret.
- **general-purpose** — design, debugging an unknown cause, review, prose, open-ended
  relevance-weighted search.

Mnemonic: needs a decision → premium; needs code understanding → mechanic; otherwise →
errand.

## Model pinning — how it works

| Path | Result |
|------|--------|
| Agent-tool `model` param | enum `{sonnet, opus, haiku, fable}` — resolves to current defaults (Sonnet 5 / current Haiku). No version pin. |
| Agent frontmatter `model:` | accepts a **full model ID** (same values as `--model`) → `claude-sonnet-4-6` / `claude-haiku-4-5` pin the exact version. |

The pin lives in shipped plugin frontmatter because that is the only place a specific
version can be selected, and a plugin makes it reproducible and shareable.

Source: [Claude Code subagents documentation](https://code.claude.com/docs/en/sub-agents.md),
section "Choose a model".

## Operational note

The agent registry is read at **session start** and is not hot-reloaded. After
installing or updating the plugin, start a **fresh session**. Verify with a one-line
spawn that returns each agent's model ID (`claude-sonnet-4-6` / `claude-haiku-4-5`).

## Model comparison

| | Haiku 4.5 (`errand`) | Sonnet 4.6 (`mechanic`) | Opus 4.8 (`general-purpose`) |
|---|---|---|---|
| In/Out per 1M | $1 / $5 | $3 / $15 | $5 / $25 |
| Context / max out | 200K / 64K | 1M / 128K | 1M / 128K |
| `effort` param | no | yes | yes (to `max`) |
