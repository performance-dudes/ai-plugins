# Doc: `mechanic` agent

The `mechanic` plugin ships a single component — the `mechanic` subagent.

## What it is

A worker pinned to **Sonnet 4.6** (`claude-sonnet-4-6`) for **mechanical,
fully-specified** tasks. It has the same broad tool access as `general-purpose`
(Read, Edit, MultiEdit, Write, Grep, Glob, Bash, NotebookEdit) but is behaviourally
constrained: it executes decided work and hands back the moment a decision is needed.

## Selecting it

```
Agent tool → subagent_type: "mechanic"
```

Give it a **fully specified** instruction. The scope is the instruction: it will not
make opportunistic changes, reformat untouched lines, or resolve ambiguity on its own.

## Model pinning — how it works

| Path | Result |
|------|--------|
| Agent-tool `model` param | enum `{sonnet, opus, haiku, fable}` — `sonnet` = Sonnet 5 (current default). No version pin. |
| Agent frontmatter `model:` | accepts a **full model ID** (same values as `--model`) → `claude-sonnet-4-6` pins 4.6. |

This is why the pin lives in a shipped plugin rather than an ad-hoc `model` argument:
the frontmatter is the only place a specific version can be selected, and a plugin
makes that pin reproducible and shareable.

Source: [Claude Code subagents documentation](https://code.claude.com/docs/en/sub-agents.md),
section "Choose a model".

## Operational note

The agent registry is read at **session start** and is not hot-reloaded. After
installing or updating the plugin, start a **fresh session** before the agent
resolves. Verify with a one-line spawn that returns its model ID — it should read
`claude-sonnet-4-6`.

## When to reach for it vs. general-purpose

- **mechanic** → the "what" is decided, only execution remains; success is objectively
  checkable. Cheaper tier, no quality loss.
- **general-purpose** (premium tier) → any judgment: design, debugging an unknown
  cause, review, prose, open-ended relevance-weighted search.
