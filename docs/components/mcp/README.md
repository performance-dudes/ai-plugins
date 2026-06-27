# Component: MCP server

> A "power socket" for external tools.

## What it is

**MCP** (Model Context Protocol) lets a plugin ship an **external server** that
gives Claude new abilities — for example query a database or call an API.

## File & format

- **File:** `example/.mcp.json` (here `.mcp.json.example`).
- **Format:** `.json` — config: which command starts the server, with which
  environment variables.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | At **session start** — the server process starts **immediately**. |
| Who triggers it? | **Automatic**, as soon as the plugin loads. |
| Where does it run? | As a separate **server process**. |

Because it auto-starts, the example ships it defused as `.example` — without a real
server the start would fail.

## In the example plugin (PR #1)

`.mcp.json.example` shows the shape: a server `example-server` started via
`node ${CLAUDE_PLUGIN_ROOT}/mcp/dist/index.js`. To run it for real, build a server
and remove the `.example` suffix.
