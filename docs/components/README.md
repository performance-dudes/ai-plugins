# Plugin components — full reference

A plugin is a **folder of building blocks**. Each block has a job and is read or
run at a specific moment. Below is every component, each with its own page:
**what it is · file & format · architecture · the real file in the example plugin ·
a runnable test**.

## The three sorts (who triggers the block?)

| Sort | Components | Trigger |
|------|-----------|---------|
| **You type something** | command, theme, output-style | you |
| **Claude decides** | skill, subagent | the model |
| **Runs automatically on load** | hooks, MCP, LSP, monitors | the program → shipped as `.example` |

## All components

| Page | Component | Status |
|------|-----------|--------|
| [manifest](manifest/README.md) | Manifest (`plugin.json`) | official |
| [marketplace](marketplace/README.md) | Marketplace (`marketplace.json`) | official |
| [command](command/README.md) | Slash command | official |
| [skill](skill/README.md) | Skill | official |
| [subagent](subagent/README.md) | Subagent | official |
| [workflow](workflow/README.md) | Workflow technique (script by path) | technique, not auto-loaded |
| [theme](theme/README.md) | Theme | experimental |
| [output-style](output-style/README.md) | Output style | official |
| [hooks](hooks/README.md) | Hooks (24+ event types) | official |
| [mcp](mcp/README.md) | MCP server | official |
| [lsp](lsp/README.md) | LSP server | official |
| [monitors](monitors/README.md) | Monitors | experimental |
| [bin](bin/README.md) | `bin/` executables | **gap** — not in the example yet |
| [settings](settings/README.md) | `settings.json` & status line | **gap** — not in the example yet |

## Why these docs are separate from `example/`

`example/` is the **running plugin** — Claude Code reads those folders to load it,
and **every `.md` in `commands/` or `agents/` becomes a command/agent**. Dropping a
`README.md` or `spec.md` in there would create bogus commands and break the
showcase. So the product (`example/`) and the documentation about it (`docs/`) stay
separate. The folder names mirror each other only for navigation.

## Each component folder contains

| File | Purpose |
|------|---------|
| `README.md` | What it is, file & format, and the architecture (when read / who triggers / where it runs). |
| `spec.md` | A user story + acceptance criteria, each with a test reference. |
| `test.sh` | A runnable check for that component. |
