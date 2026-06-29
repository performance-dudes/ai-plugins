---
name: context-aware
description: How to build context-aware Claude Code plugins — workflows and agents that route ALL retrieval through the context-mode MCP (ctx_*) so raw bytes are indexed and searched in a sandbox, never dumped into the conversation window. Domain-agnostic. Use when authoring or reviewing a plugin/workflow/agent that handles large files, command output, web pages, logs, codebases or many sources; when asked to "make a plugin context-aware", "bundle context-mode", "save the context window", "lean context", "stop reading whole files into the window", "index once search many", "fetch and index", "Think-in-Code"; or when wiring ctx_* tools into agents. Ships a runnable demo workflow (workflows/context-aware-demo.js) that implements all five patterns.
argument-hint: "[plugin or workflow to make context-aware]"
---

# context-aware — build plugins that keep raw bytes out of the window

This skill is the **source of truth** for the context-aware plugin pattern at
Performance Dudes. It is **domain-agnostic**: it teaches the technique, not any
particular subject. Use it when you author or review a plugin, workflow, or agent
that touches large data — files, shell output, web pages, logs, whole codebases,
or many sources at once.

## The principle (one paragraph)

> **Think-in-Code.** Every byte a tool returns enters the conversation and costs
> reasoning capacity for the rest of the session. So you do not *read* raw data
> into the window — you **program the analysis** in a sandbox and surface only the
> derived answer. [context-mode](https://github.com/mksglu/context-mode) is the
> MCP that provides that sandbox plus an FTS5 (BM25) knowledge base: run code,
> read files, fetch pages, index references — and pull back only `console.log()`
> output or a focused `ctx_search` slice. The raw bytes never touch the window.

## Two axes of savings

```
  Axis 1 — VERTICAL (inside one agent)        Axis 2 — HORIZONTAL (across agents)
  index a reference ONCE, slice it many        deterministic JS workflow fans out to
  times; fetch a page into the sandbox,        isolated agents; they exchange only lean
  query a derived answer out                   JSON schemas, each with a FRESH window
  → no agent re-reads whole files              → no agent pays for another's raw work
```

## The five patterns

Read the detail in `references/patterns.md`. In one line each:

1. **Index-once-slice-many** — `ctx_index` your references (SKILL, profiles,
   rulesets, specs) **once** under labelled `source` tags; every agent then pulls
   only the ~200-token slice it needs with `ctx_search`. Never `Read` a whole
   reference file into an agent.
2. **Fetch-and-index** — load web pages / API docs with `ctx_fetch_and_index`
   (HTML → markdown → chunked → FTS5), then `ctx_search` the answer out. The page
   bytes stay in the sandbox; `WebFetch` would dump them into the window.
3. **Plain-JS glue** — do dedup, fingerprinting, filtering, ranking, ledger
   bookkeeping as **deterministic code in the workflow** (or in `ctx_execute`),
   not as an LLM "thinking" step. Costs zero model tokens and is reproducible.
4. **Structured-output handoffs** — agents return **validated JSON** (a schema),
   not prose. Phase N+1 reads only the fields it needs. The handoff is tiny.
5. **Lean orchestrator** — the workflow is **code, not an agent**; it accumulates
   no transcript. The model tokens fall only in the leaf agents, and those are
   kept small.

## The ctx_* tool surface (what to call instead of what)

Full table with parameters in `references/ctx-tool-surface.md`. The reflexes:

| Instead of… | Use… | Why |
|---|---|---|
| `Bash` to gather + then parse | `ctx_batch_execute` | runs commands in parallel, auto-indexes output, returns matching sections in one round trip |
| `cat`/`Read` then reason over it | `ctx_execute` / `ctx_execute_file` | only what you `console.log()` enters the window |
| `WebFetch` a page | `ctx_fetch_and_index` | page bytes stay sandboxed; query a slice out |
| re-reading a reference each turn | `ctx_index` once + `ctx_search` | index once, slice many |
| manual memory recall | `ctx_search` (sort: timeline) | searches indexed content + session memory |

Keep `Bash`/`Read`/`WebFetch` for what they are good at: **observing** a short
fixed output, **editing** a file (Edit needs the exact bytes in the window), or
mutating state. The rule is: *process → ctx_\*; observe/mutate → native.*

## Where context-mode comes from (two valid choices)

A plugin needs the `ctx_*` tools to be present. There are two ways to arrange
that — both legitimate; pick per situation:

1. **Workspace-level dependency (what this plugin uses).** Enable
   `context-mode@context-mode` once in the workspace settings; every plugin in the
   workspace shares that one server. Leaner — no duplicate servers, nothing to
   ship. The `ctx_*` tools surface as `mcp__plugin_context-mode_context-mode__*`,
   which agents allowlist.
2. **Bundle it in the plugin.** Declare context-mode inline in `plugin.json`
   (`"mcpServers": { "context-mode": { "command": "npx", "args": ["-y",
   "context-mode"] } }`). Self-sufficient — the tools auto-start with the plugin,
   appearing as `mcp__plugin_<your-plugin>_context-mode__*`. Use when a plugin must
   work standalone outside a context-mode-enabled workspace (e.g. a CI image).

The full naming rule, both manifest shapes, the alternatives (`.mcp.json`, global
binary), and the agent `tools:` wiring are in
`references/bundling-context-mode.md`.

## How to apply this skill

When asked to make a plugin/workflow/agent context-aware:

1. **Apply pattern 1 to the references themselves** (the technique, demonstrated
   here — not a prerequisite; the skill works without it). When you expect to
   consult these references repeatedly across a long task, `ctx_index` them once,
   then `ctx_search` slices instead of re-reading whole files:
   ```
   ctx_index({ path: "${CLAUDE_PLUGIN_ROOT}/skills/context-aware/references/ctx-tool-surface.md", source: "ctxaware:tools" })
   ctx_index({ path: "${CLAUDE_PLUGIN_ROOT}/skills/context-aware/references/patterns.md",          source: "ctxaware:patterns" })
   ctx_index({ path: "${CLAUDE_PLUGIN_ROOT}/skills/context-aware/references/bundling-context-mode.md", source: "ctxaware:bundling" })
   ctx_index({ path: "${CLAUDE_PLUGIN_ROOT}/skills/context-aware/references/agent-recipes.md",     source: "ctxaware:recipes" })
   ```
   `ctx_search({ queries: ["how to bundle context-mode"], source: "ctxaware:bundling" })`
   pulls only the slice you need — the same move you are about to apply to the
   target plugin's own references.
2. **Audit the target** for the anti-patterns: `Read` of large files, `WebFetch`,
   `cat|grep` dumps, an orchestrator agent whose transcript keeps growing, prose
   handoffs between phases.
3. **Apply the patterns** in order of payoff: bundle context-mode → route
   retrieval through `ctx_*` → move glue to plain JS → make handoffs schema'd →
   pull the orchestration into a JS workflow.
4. **Copy the recipes** from `references/agent-recipes.md` for agent frontmatter
   and the system-prompt retrieval block.
5. **Show it working** — run the bundled demo:
   ```
   Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/context-aware-demo.js",
              args: { pluginRoot: "${CLAUDE_PLUGIN_ROOT}", question: "...", files: [...], urls: [...], lanes: 4 } })
   ```
   `workflows/context-aware-demo.js` is the canonical, runnable reference
   implementation of all five patterns.

## Why this matters (the cost)

Naive multi-agent work is quadratic: a monolith agent re-pays for every page and
every thought on each turn; N agents that each `Read` the same big reference pay
N× for it. Context-mode + subagent isolation turn that into: index once, slice
many, fan out to fresh windows, hand off lean JSON. The same lean-context pattern
runs the PD `cpp-pr-reviewer` and `varna-zuhause` workflows — it transfers to any
multi-source or multi-agent plugin.

References: `references/ctx-tool-surface.md` (every ctx_* tool),
`references/patterns.md` (the five patterns in depth),
`references/bundling-context-mode.md` (bundle + namespace rule + wiring),
`references/agent-recipes.md` (copy-paste frontmatter and prompt blocks).
