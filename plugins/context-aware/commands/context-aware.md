---
description: Run the context-aware demo — research a question across files and URLs, routing all retrieval through the bundled context-mode MCP (ctx_*)
argument-hint: "[question] [source ...]  (sources are file paths and/or URLs)"
---

# /context-aware — context-aware research, by example

Run the plugin's bundled demo workflow for `$ARGUMENTS`. It demonstrates the
context-aware pattern end-to-end: index the sources **once**, fan out scout
agents that pull only the slices they need via `ctx_search`, dedup their findings
in plain JS, and synthesize a structured report — **no raw file or page bytes
ever enter the conversation**.

## Step 1 — parse the request

From `$ARGUMENTS`, separate:

- **question** — the first quoted string, or everything up to the first source.
- **sources** — the remaining tokens. A token is a **URL** if it starts with
  `http://` / `https://`, otherwise a **file path** (relative to the user's
  project). If no sources are given, ask the user for at least one.

## Step 2 — run the workflow

**Preferred — Workflow orchestration.** If the **Workflow tool** is available,
invoke the bundled script. `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin's
install directory regardless of where it was installed:

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/context-aware-demo.js",
  args: {
    pluginRoot: "${CLAUDE_PLUGIN_ROOT}",
    question: "<the question>",
    files:    ["<file path>", ...],
    urls:     ["<url>", ...],
    lanes:    4
  }
})
```

The workflow:
1. **Index** — one agent indexes the files with `ctx_index` and fetches the URLs
   with `ctx_fetch_and_index` (raw bytes stay in the sandbox), then splits the
   question into sub-questions.
2. **Scout** — fans out one agent per sub-question; each `ctx_search`-es the
   indexed corpus and returns lean JSON findings.
3. **Dedup** — plain JS merges findings by fingerprint (no LLM).
4. **Synthesize** — one agent turns the deduped findings into a structured
   report, `ctx_search`-ing only to fill gaps.

When the task-notification arrives, report the returned `report` (summary, key
points, gaps, sources used) and mention how many findings were deduped.

**Fallback (no Workflow tool).** Do the same flow yourself, but still
context-aware: `ctx_index` the files and `ctx_fetch_and_index` the URLs first,
then `ctx_search` per sub-question — never `Read` whole files or `WebFetch` whole
pages into the window. Step-by-step: `${CLAUDE_PLUGIN_ROOT}/skills/context-aware/SKILL.md`.

## Prerequisites

The `ctx_*` tools come from the context-mode MCP, enabled once at the workspace
level (this plugin does not bundle it). If they are missing, run
`/context-aware-doctor`.
