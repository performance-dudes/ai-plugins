# The context-mode tool surface (ctx_*)

Every tool the context-mode MCP exposes, what it is for, its key parameters, and
when to reach for it instead of a native tool. The fully-qualified MCP name is
`mcp__plugin_<host-plugin>_context-mode__<tool>`. With the workspace-level
context-mode plugin (what this plugin relies on) that is
`mcp__plugin_context-mode_context-mode__<tool>`; if a plugin instead bundles its
own copy, the host-plugin segment is that plugin's name. In agent prompts you can
refer to them by short name (`ctx_search`, `ctx_index`, …).

## Contents

- The golden rule
- Gather & process — `ctx_batch_execute`, `ctx_execute`, `ctx_execute_file`, `ctx_fetch_and_index`
- Knowledge base — `ctx_index`, `ctx_search`
- Diagnostics & management — `ctx_stats`, `ctx_doctor`, `ctx_upgrade`, `ctx_purge`, `ctx_insight`
- Where the data lives
- Session memory (free, automatic)

## The golden rule

> **process → ctx_\*  ·  observe/mutate → native.**
> If you will filter, count, parse, aggregate, transform, or search the output,
> route it through `ctx_*` so the raw bytes stay in the sandbox. Keep `Bash` for a
> short fixed output you just want to *see* (a clean `git status`, `pwd`), for
> *mutating* state (git, mkdir, mv, rm), and keep `Read` for a file you are about
> to `Edit` (Edit needs the exact bytes in the window).

## Gather & process

### ctx_batch_execute — the primary research tool
Run several shell commands **in parallel**, auto-index each output, and (when you
pass `queries`) return the matching sections in the **same** round trip.
- `commands`: `[{ label, command }, …]` — `label` becomes the FTS5 chunk title,
  so make labels descriptive ("changed files", "test failures").
- `queries`: optional `[…]` — questions answered against what the commands just
  produced.
- `concurrency` (1–8), `query_scope` (`"batch"` | `"global"`), `cwd`, `timeout`.
- **Use when:** 3+ related commands, or gather-then-ask in one call. Replaces a
  long sequence of `Bash` + manual reading.

### ctx_execute — run code, surface only what you log
Execute code in 11+ languages (javascript, python, shell, ruby, go, rust, php,
perl, r, elixir, c#) in a sandboxed subprocess. Only `console.log()` / `print()`
output enters the window.
- `language`, `code`, optional `timeout`, `intent` (label for auto-indexing big
  output), `background` (for servers/daemons).
- **Use when:** computing, filtering, aggregating, parsing JSON, transforming. The
  workhorse for "derive an answer from data" without importing the data.

### ctx_execute_file — run code over a file without reading it in
Load a file into the sandbox (exposed as a `FILE_CONTENT` variable) and run code
over it. The raw bytes stay in the subprocess.
- `path`, `language`, `code`, optional `intent`, `timeout`.
- **Use when:** analyzing / extracting / summarizing a large file. Use native
  `Read` only when you will `Edit` it afterwards.

### ctx_fetch_and_index — fetch the web into the sandbox
Fetch one or more URLs, convert HTML → markdown, chunk, and index into FTS5.
- Single: `url`, `source`, optional `ttl` (seconds; `0` bypasses cache), `force`.
- Batch: `requests: [{ url, source }, …]`, `concurrency` (1–8).
- **Use when:** any web doc, API reference, changelog, listing page. Replaces
  `WebFetch` entirely — page bytes never enter the window; you `ctx_search` the
  derived answer out afterwards.

## Knowledge base

### ctx_index — store references for later slicing
Chunk markdown/text by headings (code blocks kept intact), store in FTS5 with
BM25 weighting (titles weighted ~5×).
- `content` **or** `path`, plus `source` (a label you query against later).
- Directory mode: `include` / `exclude` globs, `maxDepth`, `maxFiles`,
  `respectGitignore`, `extensions`.
- **Use when:** loading SKILLs, profiles, rulesets, specs, READMEs **once** so many
  agents can `ctx_search` slices instead of re-reading the whole file.

### ctx_search — pull a slice out
Query the unified knowledge base (your indexed content **and** auto-captured
session memory). Multi-strategy ranking (Porter stemming + trigram + RRF merge).
- `queries`: `[…]` — batch every related question in one call; ranking runs
  per-query, round-trip paid once.
- `limit` (results per query, default ~3), `sort` (`"relevance"` | `"timeline"`),
  `source` (restrict to a label), `contentType` (`"code"` | `"prose"`).
- **Use when:** recalling anything already indexed — references, fetched pages,
  prior-session decisions. `sort: "timeline"` spans current + prior sessions
  (memory recall).

## Diagnostics & management

| Tool | Purpose | Params |
|---|---|---|
| `ctx_stats` | context savings this session (bytes saved, ratio, per-tool breakdown) | none |
| `ctx_doctor` | diagnose install: runtimes, hooks, FTS5, plugin registration | none |
| `ctx_upgrade` | update context-mode from source; returns a shell command to run | none |
| `ctx_purge` | delete indexed content — destructive | `confirm: true`, `scope: "session"\|"project"`, `sessionId?` |
| `ctx_insight` | open the hosted Insight analytics dashboard | none |

## Where the data lives

The FTS5 knowledge base is local and on disk under `$CONTEXT_MODE_DIR` (default
`~/.claude/context-mode/`): `sessions/` holds the per-project session event log,
`content/` holds the indexed FTS5 chunks. Nothing leaves the machine (except a
`ctx_fetch_and_index` actually fetching a URL, and `ctx_insight` opening a
browser). Indexed content persists across `/clear` and `/compact` — purge with
`ctx_purge` to start fresh.

## Session memory (free, automatic)

context-mode auto-captures file edits, git ops, tasks, errors, decisions, and
tool calls into FTS5. After a compaction or on resume, `ctx_search({ sort:
"timeline" })` recalls prior decisions/errors/plans **before** asking the user —
the raw history is searchable without being re-dumped into the window.
