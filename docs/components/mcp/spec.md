# Spec: MCP-server component

**Theme:** The plugin ships a defused MCP template that shows how to wire a bundled
external server.

## US-MCP-1 — A defused MCP template

> As a **plugin author**, I want a defused MCP template, so that I can see how a
> bundled server is wired without anything auto-starting.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-MCP-1-1 | The template exists at `example/.mcp.json.example`. | `test.sh` (file presence) |
| AC-MCP-1-2 | It is valid JSON. | `test.sh` (`python3 -m json.tool`) |
| AC-MCP-1-3 | It declares `mcpServers`. | `test.sh` (grep) |
