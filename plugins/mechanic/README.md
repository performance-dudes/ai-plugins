# mechanic

A cost-tiered subagent for **mechanical, fully-specified execution** — pinned to the
cheaper **Sonnet 4.6** tier so the premium tier (Opus / Sonnet 5) stays free for
work that needs judgment.

## Why

Sonnet 4.6 is the previous, cheaper Sonnet generation (≈ $3/$15 per 1M tokens vs.
the pricier Sonnet 5). For **deterministic** work — a task with a single correct
output — the cheaper tier is enough. Routing that work here is a straight budget win
with no quality loss, because there is no judgment to lose.

## When to use

Invoke via the Agent tool with `subagent_type: "mechanic"` when the task is
**already decided** and success is objectively checkable:

- apply a specified edit across one or many files
- search-and-replace, rename a symbol, reorder/sort, reformat
- generate boilerplate/scaffolding from a given shape
- move/rename/copy files; mechanical refactors with a stated rule
- extract a value, run a known command and report its output

## When NOT to use

Route to `general-purpose` (or a specialist) on the premium tier whenever the task
needs a **decision**: design, architecture, naming choices, debugging an unknown
cause, correctness/security review, writing prose or specs, or open-ended search
where relevance must be weighed. **If the task needs a decision, it is not
mechanical.** The agent is instructed to hand back rather than guess.

## Model pin

The agent pins `model: claude-sonnet-4-6` in its frontmatter. Claude Code's `model:`
field accepts a full model ID (same values as the `--model` flag), so this selects
Sonnet 4.6 specifically rather than the generic `sonnet` alias (which resolves to
the current default, Sonnet 5). See
[Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents.md).

## Install

```bash
claude plugin marketplace add performance-dudes/ai-plugins
```

Then enable `mechanic@ai-plugins` in your workspace `enabledPlugins`. A **fresh
session** is required for a newly installed/updated agent to load (the agent
registry is read at session start, not hot-reloaded).
