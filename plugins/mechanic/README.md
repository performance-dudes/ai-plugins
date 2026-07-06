# mechanic

Cost-tiered subagents for **mechanical, fully-specified work** — two agents pinned to
cheaper model versions so the premium tier (Opus / Sonnet 5) stays free for judgment.

| Agent | `subagent_type` | Model pin | For |
|---|---|---|---|
| `mechanic` | `mechanic` | `claude-sonnet-4-6` | mechanical work that needs **code/context comprehension** |
| `errand` | `mechanic:errand` | `claude-haiku-4-5` | **trivial, self-contained** transformations, no codebase understanding |

## Why

Sonnet 4.6 (≈ $3/$15 per 1M) is cheaper than Sonnet 5; Haiku 4.5 (≈ $1/$5) is cheaper
still. **Deterministic** work — a single correct output — doesn't need a premium
model, so routing it down is a straight budget win with no quality loss. The only
question is *which* cheap tier, and that's decided by how much understanding the task
needs.

## The routing rule

```
Needs a DECISION (design, debug unknown cause, review, prose, weigh relevance)
    -> general-purpose (premium tier)

Needs to UNDERSTAND CODE/CONTEXT to execute a decided change
    -> mechanic            (subagent_type "mechanic", Sonnet 4.6)

TRIVIAL self-contained transformation, no codebase understanding
    -> errand              (subagent_type "mechanic:errand", Haiku 4.5)
```

- **`errand`** — classify/label, extract a field, reformat (JSON/CSV/whitespace/case),
  literal find/replace with an exact old→new pair, yes/no checks, count, sort, normalize.
- **`mechanic`** — apply a specified edit that must fit its surroundings, mechanical
  refactor across files, generate boilerplate that must slot into an existing codebase,
  run a known command and interpret its output.

Both agents are instructed to **hand back rather than guess** when a task turns out to
sit in a neighbouring tier or the instruction is ambiguous.

## Model pins

Each agent pins a full model ID in its frontmatter. Claude Code's `model:` field
accepts a full model ID (same values as the `--model` flag), so this selects the exact
version rather than a generic alias (`sonnet` → Sonnet 5, `haiku` → current default).
See [Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents.md).

## Install

```bash
claude plugin marketplace add performance-dudes/ai-plugins
```

Enable `mechanic@ai-plugins` in your workspace `enabledPlugins`. A **fresh session** is
required for newly installed/updated agents to load (the agent registry is read at
session start, not hot-reloaded).
