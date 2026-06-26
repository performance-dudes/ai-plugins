# example — Claude Code plugin techniques, by example

A copy-me reference plugin that demonstrates **every plugin component type** and
the **techniques** for wiring them together — plus how to **test** plugins and
skills.

## Component map

| Component | Path | Status | Shows |
|-----------|------|--------|-------|
| Manifest | `.claude-plugin/plugin.json` | active | required fields |
| **Workflow** | `workflows/greet.js` | active | dynamic workflow bundled in a plugin |
| **Slash command** | `commands/greet.md` | active | `/greet` → invokes the workflow by `scriptPath` |
| **Skill** | `skills/run-greet/SKILL.md` | active | skill that calls the same workflow autonomously |
| **Subagent** | `agents/greeter.md` | active | `subagent_type: "greeter"`, least-privilege tools |
| **Theme** | `themes/performance-dudes.json` | active (opt-in) | `/theme` custom colors |
| **Output style** | `output-styles/terse.md` | active (opt-in) | `/output-style` system-prompt overlay |
| Hooks | `hooks/hooks.json.example` | template | PreToolUse hook + script |
| MCP server | `.mcp.json.example` | template | bundled MCP server wiring |
| LSP server | `.lsp.json.example` | template | language-server config |
| Monitors | `monitors/monitors.json.example` | template | background monitor (experimental) |
| Tests | `tests/` | — | how to validate & test all of the above |

### Why some components are `.example` templates

"active (opt-in)" components (theme, output style) and on-demand ones (command,
skill, agent, workflow) are **safe to enable** — nothing runs until you ask.

Hooks, MCP, LSP and monitors **auto-activate** the moment the plugin loads and
need external binaries/servers. They ship as `*.example` so the showcase is safe
to enable as-is. To try one, drop the `.example` suffix and provide its binary.

## The core technique: a plugin-bundled workflow

Named-workflow resolution (`Workflow({ name })`) only knows built-ins and the
files in `~/.claude/workflows` / `.claude/workflows` **at session start** — it
does **not** discover plugin scripts. So a plugin ships its script in
`workflows/` and invokes it **by path** from a command or skill:

```js
Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/greet.js", args: "$ARGUMENTS" })
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the install dir, so the same call works
everywhere. This is the pattern Anthropic's official `code-modernization` plugin
uses. (`${CLAUDE_PLUGIN_DATA}` = persistent data dir; `${CLAUDE_PROJECT_DIR}` =
the user's project.)

## Try it

```
/greet Felix
```

or just ask: *"greet the Performance Dudes"* (the `run-greet` skill triggers).

## Testing

See `tests/README.md` and run:

```bash
bash example/tests/validate.sh
```
