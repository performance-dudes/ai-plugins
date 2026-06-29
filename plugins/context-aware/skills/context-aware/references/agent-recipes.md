# Agent recipes — copy-paste frontmatter and prompt blocks

Drop-in shapes for context-aware agents and workflows. Adapt the names; keep the
retrieval discipline.

## Contents

- Recipe A — a fan-out finder/scout agent
- Recipe B — a synthesizer agent (reads lean JSON, fills gaps)
- Recipe C — the reusable retrieval block (inject into every agent prompt)
- Recipe D — workflow skeleton (the lean orchestrator)
- Do / Don't
- Constraints to remember in workflows

## Recipe A — a fan-out finder/scout agent

```markdown
---
name: <your>-scout
description: >
  Pure recall-first finder for ONE sub-question over a PRE-INDEXED corpus. Routes
  ALL retrieval through context-mode (ctx_*) — never Reads whole files or WebFetches
  raw pages. Returns a single validated JSON object {"findings":[...]}. Read-only.
model: sonnet
maxTurns: 12
tools:
  - Read
  - Bash
  - Grep
  - Glob
  - mcp__plugin_context-mode_context-mode__*   # workspace-level context-mode (Option A)
  # if you BUNDLE context-mode (Option B), also add: mcp__plugin_<your-plugin>_context-mode__*
---

# <your>-scout

You answer ONE sub-question against an already-indexed corpus.

> **context-mode (ctx_*) is your retrieval substrate (bundled with this plugin).**
> Pull what you need with `ctx_search` (one bundled call, scope by `source`). Load
> any URL with `ctx_fetch_and_index`, then `ctx_search` the answer out — NEVER
> WebFetch or Read raw bytes into your window. Use `ctx_execute` to filter/parse.
> Pull only small metadata (a filename, a line count) directly.

Return EVERY candidate finding for your sub-question — do not self-filter. One
finding ↔ one claim ↔ one source. Emit a `fingerprint` (`source|claim-prefix`) so
the workflow can dedup deterministically. Your final message is the JSON return
value — no prose.
```

## Recipe B — a synthesizer agent (reads lean JSON, fills gaps)

```markdown
---
name: <your>-synthesizer
description: >
  Turns a deduped set of lean JSON findings into a structured report. Reads the
  findings it is handed; uses ctx_search ONLY to fill specific gaps. Returns one
  validated JSON object. Read-only.
model: opus
maxTurns: 10
tools:
  - mcp__plugin_context-mode_context-mode__*   # workspace-level context-mode (Option A)
---

# <your>-synthesizer

You receive a deduped findings array (already lean — do not re-fetch the sources).
Synthesize a structured report. If a specific fact is missing, `ctx_search` the
indexed corpus for just that fact — do not Read whole files or re-fetch pages.
Return the report as the JSON schema you were given. No prose outside the JSON.
```

## Recipe C — the reusable retrieval block (inject into every agent prompt)

Workflows build this once and pass it into each leaf agent's prompt, so the agent
gets the *discipline* without the file contents:

```js
const READ = `Pull references from context-mode — they are PRE-INDEXED (do NOT Read the whole
files, that bloats the window). One bundled ctx_search call, scope by source:
  ${sources.map(s => `  ${s.tag}  (${s.desc})`).join("\n")}
Load any web page with ctx_fetch_and_index, then ctx_search it — never raw HTML in the window.
Fallback ONLY if ctx_search returns empty: Read the one specific file you need.`
```

## Recipe D — workflow skeleton (the lean orchestrator)

```js
export const meta = {
  name: "<your>-flow",
  description: "index-once -> fan-out -> JS-dedup -> synthesize, all retrieval via ctx_*",
  phases: [{ title: "Index" }, { title: "Scout" }, { title: "Synthesize", model: "opus" }],
}

const a = (args && typeof args === "object") ? args : {}
const root = a.pluginRoot || "."

// Phase Index — index refs + fetch URLs ONCE (raw bytes -> sandbox)
phase("Index")
await agent(
  `Index these into context-mode (one ctx_index per file; ctx_fetch_and_index per URL). Return "ok".
   ${refs.map(r => `ctx_index({ path: "${r.path}", source: "${r.tag}" })`).join("\n")}`,
  { label: "index", phase: "Index" }
).catch(() => null)

// Phase Scout — fan out one agent per sub-question (BARRIER: need all before dedup)
phase("Scout")
const found = (await parallel(subqs.map(q => () =>
  agent(`${READ}\n\nSub-question: ${q}\nReturn findings as JSON.`,
        { label: `scout:${q.slice(0,24)}`, phase: "Scout", schema: FINDINGS_SCHEMA })
))).filter(Boolean).flatMap(r => r.findings)

// Dedup — plain JS, no agent
const deduped = dedupeByFingerprint(found)

// Phase Synthesize — one agent reads lean JSON, ctx_search for gaps
phase("Synthesize")
const report = await agent(
  `${READ}\n\nFindings (deduped JSON):\n${JSON.stringify(deduped)}\n\nSynthesize the report as JSON.`,
  { label: "synth", phase: "Synthesize", schema: REPORT_SCHEMA }
)
return { report, findings: deduped.length }
```

## Do / Don't

| Do | Don't |
|---|---|
| `ctx_index` a reference once, `ctx_search` slices | `Read` a whole reference into every agent |
| `ctx_fetch_and_index` a URL, then `ctx_search` | `WebFetch` a page into the window |
| `ctx_execute` to filter/aggregate | `cat file | grep | ...` dumped via Bash |
| force agents to a `schema` | let agents hand off prose |
| dedup/rank/ledger in plain JS | ask an LLM "are these the same?" |
| orchestrate in a JS workflow | nest sub-agents under one growing manager agent |
| allowlist the ctx_* namespace the workspace actually exposes | hardcode a bundled namespace the plugin doesn't ship |

## Constraints to remember in workflows

`Date.now()`, `Math.random()`, and argless `new Date()` are **unavailable** in
workflow scripts (they would break resume) — pass timestamps via `args`, vary
agent labels by index for uniqueness. `agent()` without a `schema` returns a
string; with a `schema` it returns the validated object (or `null` if the agent
died — `.filter(Boolean)`). Prefer `pipeline()`; use `parallel()` only when a
stage truly needs all prior results (e.g. a global dedup before synthesis).
