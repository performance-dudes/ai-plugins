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

TRIVIAL transformation, no codebase understanding — as a BATCH / at volume
    -> errand              (subagent_type "mechanic:errand", Haiku 4.5)

TRIVIAL transformation, but a SINGLE small item
    -> INLINE — do it yourself, do NOT delegate
```

- **inline** — one JSON snippet to format, one field to read, one yes/no check, one
  literal edit at a named spot. Delegating a lone trivial task loses money: an agent
  run burns ~4× the tokens of a plain turn (spawn + context transfer + reintegration),
  which outweighs the cheap-model saving on a single item. Keep it in the orchestrator.
- **`errand`** — the SAME trivial ops, but **at volume**: classify 800 lines, reformat
  240 files, extract from 500 log rows, normalize a 12k-row CSV, scan 900 docs. Now the
  cheap-model saving amortises over the batch and delegating wins.
- **`mechanic`** — apply a specified edit that must fit its surroundings, mechanical
  refactor across files, generate boilerplate that must slot into an existing codebase,
  run a known command and interpret its output.
- **`general-purpose`** — design, debug an unknown cause, review, a naming/architecture
  choice, prose/specs. No single correct output; needs judgement.

Both agents are instructed to **hand back rather than guess** when a task turns out to
sit in a neighbouring tier, is a lone item that belongs inline, or the instruction is
ambiguous.

### Prefer one tier too expensive over one too cheap

The routing error is **asymmetric**. Over-provisioning (routing up) just spends a bit
more. **Under-provisioning (routing down) is the expensive mistake**: a too-cheap tier
that isn't up to the task fails, and you pay for the failed cheap attempt **plus** the
retry at the correct tier — the cascade pays cheap+strong, never just strong, and
small/large model errors are correlated so the query the cheap model flubs is
disproportionately a hard one. So when in doubt, **round up a tier**. The eval tracks
this as a first-class **under-routing rate**, separate from plain accuracy.

## Evals — is the routing actually sharp?

The plugin's whole value is a **correct routing decision**, so that is what
[`evals/`](evals/README.md) measures — not that the agents load, but that a task
lands in the right tier. `evals/routing/ground_truth.yaml` holds locked, diverse
cases across all four outcomes (inline · errand · mechanic · general-purpose), each
with a deliberate near-miss `trap` (the tempting wrong neighbour). The output is a
label, so the regime is deterministic: `evals/scripts/score_routing.py` builds a
confusion matrix and reports **accuracy · macro-F1 · under-routing rate**, plus an
illustrative **cost model** (baseline all-premium → routed, with a retry penalty for
under-routing) that answers "how much do we save, and how much does a too-cheap route
cost us?".

**The one rule:** the eval tests the **plugin** (these agent descriptions, this
routing rule). A misroute is a bug to fix *here* — sharpen a description — never a
case to loosen so the run goes green. See [`evals/README.md`](evals/README.md).

## Model pins

Each agent pins a full model ID in its frontmatter. Claude Code's `model:` field
accepts a full model ID (same values as the `--model` flag), so this selects the exact
version rather than a generic alias (`sonnet` → Sonnet 5, `haiku` → current default).
See [Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents.md).

## Tool access

Neither agent declares a `tools:` allow-list, so both inherit the **full tool set of
the session** — the same broad access `general-purpose` has: file/search/edit tools,
Bash, web tools, **and every MCP server the session exposes** (Playwright, context-mode,
Gmail, Calendar, and so on). Most MCP tools are **deferred**: their schemas load on
demand, so an agent fetches what it needs with `ToolSearch` before calling it (batch
every tool into one `select:` query). A pinned `tools:` list would have silently
excluded MCP and `ToolSearch`, which is why there is none.

Broad tool access is **not** broad scope. The cost tier is enforced by the model pin
and the agent's contract, not by withholding tools: `errand` still does one trivial
transformation, `mechanic` still executes a decided change, and both still hand back
the moment a task needs a decision. MCP is there for when the mechanical task genuinely
needs it (read a sheet, drive a page, pull a message), not as licence to widen the job.

## Install

```bash
claude plugin marketplace add performance-dudes/ai-plugins
```

Enable `mechanic@ai-plugins` in your workspace `enabledPlugins`. A **fresh session** is
required for newly installed/updated agents to load (the agent registry is read at
session start, not hot-reloaded).
