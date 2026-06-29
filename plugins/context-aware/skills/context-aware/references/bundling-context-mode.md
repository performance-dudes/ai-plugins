# Bringing context-mode to a plugin (two ways)

A context-aware plugin needs the `ctx_*` tools present. There are two valid ways
to arrange that, and the namespace the tools land under differs between them — get
that right and the agent `tools:` wiring follows.

## Contents

- Option A — workspace-level dependency (what THIS plugin uses)
- Option B — bundle it in the plugin (self-sufficient)
- The namespace rule
- Wiring agents to the tools
- Bundling variants (for Option B)
- Verifying it (doctor)
- Self-update

## Option A — workspace-level dependency (leaner; what THIS plugin uses)

Enable the standalone `context-mode@context-mode` plugin **once** in the workspace
settings; every plugin in the workspace then shares that one server. Nothing to
ship in your plugin, and no duplicate servers.

```jsonc
// performance-dudes/.claude/settings.json
{ "enabledPlugins": { "context-mode@context-mode": true } }
```

Enable once per machine:

```
claude plugin marketplace add mksglu/context-mode
claude plugin install context-mode@context-mode
```

The tools surface under `mcp__plugin_context-mode_context-mode__*` — that is the
single namespace this plugin's agents allowlist. **Prefer this** for plugins that
live inside a context-mode-enabled workspace (all PD plugins do).

## Option B — bundle it in the plugin (self-sufficient)

When a plugin must work **standalone** outside a context-mode-enabled workspace
(e.g. a constrained CI image), it can ship context-mode itself. Declare it as an
inline MCP server in `.claude-plugin/plugin.json` — no separate file, no path,
fetched on demand from npm:

```json
{
  "name": "context-aware",
  "version": "0.1.0",
  "description": "...",
  "mcpServers": {
    "context-mode": {
      "command": "npx",
      "args": ["-y", "context-mode"]
    }
  }
}
```

- `command: "npx"` + `args: ["-y", "context-mode"]` runs `npx -y context-mode`,
  which fetches and launches the published `context-mode` npm package (auto-yes).
- Nothing is vendored into the plugin; the npm cache warms on first run (needs
  network once). This is the pattern the PD `cpp-pr-reviewer` specifies for
  bundling its retrieval substrate.

When the plugin loads, Claude Code starts the server and exposes its tools.

## The namespace rule (important)

A plugin-provided MCP tool is named:

```
mcp__plugin_<host-plugin-name>_<server-key>__<tool>
```

So the **same** context-mode server surfaces under **different** namespaces
depending on which plugin started it:

| How context-mode is loaded | host-plugin | server-key | resulting tool namespace |
|---|---|---|---|
| standalone `context-mode@context-mode` plugin (Option A) | `context-mode` | `context-mode` | `mcp__plugin_context-mode_context-mode__*` |
| bundled by a plugin named e.g. `acme` (Option B) | `acme` | `context-mode` | `mcp__plugin_acme_context-mode__*` |

This plugin uses Option A, so its agents allowlist the first namespace. A plugin
that bundles (Option B) allowlists the second — named after itself — so if you
rename a bundling plugin, its namespace changes with it; update the agents'
allowlist to match. A plugin that supports either arrangement lists both.

> Two copies running at once (bundled **and** standalone) is harmless — they are
> the same server binary over the same on-disk store. The agent simply has two
> equivalent namespaces available.

## Wiring agents to the tools

In each agent's frontmatter, allowlist the context-mode tools by wildcard. This
plugin uses **Option A**, so it lists the single standalone namespace:

```yaml
---
name: context-scout
model: sonnet
tools:
  - Read
  - Bash
  - Grep
  - Glob
  - mcp__plugin_context-mode_context-mode__*      # Option A — the workspace-level plugin
---
```

If instead you **bundle** (Option B), the namespace is named after *your* plugin,
so allowlist that — and if a plugin should work under **either** arrangement, list
**both** (unmatched patterns are ignored, so listing both is safe):

```yaml
  - mcp__plugin_<your-plugin>_context-mode__*     # Option B — the bundled copy
  - mcp__plugin_context-mode_context-mode__*      # Option A — workspace-level, if also enabled
```

Commands that may call `ctx_*` directly (e.g. a fallback path) put the same
wildcard(s) in their `allowed-tools:` line.

## Bundling variants (for Option B)

If you do bundle (Option B), these are the manifest shapes, strongest first:

| Approach | Shape | When |
|---|---|---|
| **inline `mcpServers` in plugin.json** | `npx -y context-mode` | default for bundling — self-sufficient, one file, auto-starts on load |
| separate `.mcp.json` at plugin root | same JSON in `.mcp.json` | when you prefer the MCP config out of the manifest; also auto-starts |
| global binary | `"command": "context-mode"` | when context-mode is `npm i -g`'d and you want to avoid npx latency |
| `node ${CLAUDE_PLUGIN_ROOT}/start.mjs` | vendored copy | only if you vendor context-mode into the plugin (heavy; not recommended) |

The example plugin ships a `.mcp.json.example` template (renamed to activate) to
keep its showcase inert. **This** plugin lives in a context-mode-enabled workspace,
so it needs none of the above — it uses Option A and ships **no** MCP config at
all. Reach for Option B only when a plugin must run where no workspace-level
context-mode exists.

## Verifying it (doctor)

`scripts/doctor.sh` checks the dependency without installing anything:

- `node >= 20` and `claude` — required for the Workflow tool and agent passes.
- the **context-mode plugin** is enabled (`claude plugin list | grep context-mode`)
  — required, since this plugin relies on the workspace-level server (Option A). A
  miss prints the exact enable commands.

(If you instead bundle context-mode — Option B — the doctor would check `npx`
resolves the package rather than the plugin being enabled.)

## Self-update

The context-mode relay keeps itself current; `npx -y context-mode` always
resolves the latest published version on a cold cache. To pin a version, set
`args: ["-y", "context-mode@<version>"]`. To update a warm cache manually, run
`npx -y context-mode@latest` once or use the `ctx_upgrade` tool.
