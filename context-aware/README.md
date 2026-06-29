# context-aware — build plugins that keep raw bytes out of the window

A copy-me reference plugin that shows how a Claude Code plugin makes its
**workflows and agents context-aware**: every retrieval — files, shell output,
web pages, prior findings — is routed through the bundled
[context-mode](https://github.com/mksglu/context-mode) MCP (`ctx_*`) so the raw
bytes are **indexed and searched in a sandbox, never dumped into the
conversation**. Only the derived answer reaches the model.

It **relies on the context-mode MCP**, which is enabled **once at the workspace
level** (not bundled per plugin — that keeps every plugin lean and avoids running
several copies of the same server). The bundling alternative is still *taught* in
the references, because it is a legitimate technique — this plugin simply chooses
the workspace-level dependency instead.

```
  ❌ naive plugin                         ✅ context-aware plugin
  ┌───────────────────────┐             ┌────────────────────────────────┐
  │ agent Read()s files,  │             │ workflow = plain JS (≈0 tokens) │
  │ WebFetch()es pages,   │             │   index once · dedup · handoff  │
  │ cat|grep dumps —       │            └──────────┬─────────────────────┘
  │ window grows & grows  │                        │ lean JSON
  │ → quadratic cost      │             ┌──────────┴───────────┐
  └───────────────────────┘             ▼          ▼           ▼
                                      scout      scout       scout   ← fresh window each
                                     ctx_search ctx_search  ctx_search  (only slices in)
```

## The core idea

> **Think-in-Code.** Program the analysis; do not compute it by reading raw data
> into your conversation. Every byte a tool returns costs reasoning capacity for
> the rest of the session. context-mode does the work in a sandbox and surfaces
> only the result.

This plugin turns that idea into a repeatable plugin-authoring pattern, on two
axes:

- **Vertical (inside one agent):** large references are indexed **once**, then
  each agent pulls only the ~200-token **slice** it needs via `ctx_search`; whole
  web pages are loaded with `ctx_fetch_and_index` and queried, never read raw.
- **Horizontal (across agents):** a deterministic JS workflow fans out to
  isolated agents that exchange only **lean JSON schemas** — no agent pays for
  another's raw work.

## Components

| Component | Path | Shows |
|-----------|------|-------|
| **Manifest** | `.claude-plugin/plugin.json` | lean manifest; context-mode is a workspace-level dependency |
| **Skill** | `skills/context-aware/SKILL.md` | the agnostic how-to: build context-aware plugins |
| References | `skills/context-aware/references/` | the ctx_* tool surface, the 5 patterns, the bundling crux, agent recipes |
| **Workflow** | `workflows/context-aware-demo.js` | runnable demo: index-once → plan → fan-out scouts → JS-dedup → synthesize |
| **Subagents** | `agents/context-scout.md`, `agents/context-synthesizer.md` | retrieval routed through ctx_* only |
| **Command** | `commands/context-aware.md` | `/context-aware` → runs the demo on any sources |
| Command | `commands/context-aware-doctor.md` | `/context-aware-doctor` → dependency preflight |
| Tests | `tests/validate.sh` | static + syntax validation |

## Try it

```
/context-aware "What changed in this repo recently?" ./CHANGELOG.md ./README.md
```

or point it at URLs and files together:

```
/context-aware "Summarize the API" ./openapi.yaml https://example.com/docs
```

or just ask: *"research this question across these sources, context-aware"* — the
`context-aware` skill triggers.

Check your environment first:

```
/context-aware-doctor
```

## Where context-mode comes from

This plugin does **not** bundle context-mode — it expects the
`context-mode@context-mode` plugin to be enabled **once at the workspace level**
(`performance-dudes/.claude/settings.json` → `enabledPlugins`). Its `ctx_*` tools
then surface under `mcp__plugin_context-mode_context-mode__*`, which is what the
demo agents allowlist.

Enable it once per machine:

```
claude plugin marketplace add mksglu/context-mode
claude plugin install context-mode@context-mode
```

> **Bundling is also possible** (a plugin can ship context-mode inline via
> `"mcpServers": { "context-mode": { "command": "npx", "args": ["-y", "context-mode"] } }`),
> and the references **teach** that technique and its namespace rule — but this
> plugin deliberately uses the leaner workspace-level dependency. Full detail:
> [`references/bundling-context-mode.md`](skills/context-aware/references/bundling-context-mode.md).

## Why a skill *and* a command

- `commands/context-aware.md` is the explicit `/context-aware` entry point.
- The skill lets the model invoke the same demo workflow autonomously when a
  request matches, and — more importantly — is the **teaching surface**: it and
  its references are the source of truth for the context-aware plugin pattern.

Both funnel into one `workflows/context-aware-demo.js` — single source of truth.

## Testing

```bash
bash context-aware/tests/validate.sh
```
