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
| **Skill reference** | `skills/run-greet/references/advanced-greetings.md` | active | lazy-loaded detail a skill reads only on demand |
| **Subagent** | `agents/greeter.md` | active | `subagent_type: "greeter"`, least-privilege tools |
| **Theme** | `themes/performance-dudes.json` | active (opt-in) | `/theme` custom colors |
| **Output style** | `output-styles/terse.md` | active (opt-in) | `/output-style` system-prompt overlay |
| Hooks | `hooks/hooks.json.example` | template | PreToolUse + PostToolUse hooks + scripts |
| Settings / permissions | `.claude/settings.json.example` | template | `permissions` allow/ask/deny + `enabledPlugins` |
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

## Lazy-loaded skill references

A skill's `SKILL.md` is always loaded, so it should stay short. Detail that the
model needs only *sometimes* goes in a sibling `references/` folder and is read
**on demand** — here `skills/run-greet/references/advanced-greetings.md` holds
greeting styles, localization notes and edge cases. `SKILL.md` links to it; the
model opens it only when a request actually needs that depth. This keeps the
always-on instruction footprint small while deep material stays one hop away.

## Multiple hook event types

`hooks/hooks.json.example` wires up **two** events on the same `Bash` matcher to
show that a plugin is not limited to one: `PreToolUse` fires *before* a tool runs
and can block it (exit 2), while `PostToolUse` fires *after* and also sees the
tool's result — useful for logging or follow-up context, but it cannot un-run the
call. Each event points at its own script under `hooks/scripts/`. Same template
caveat as the other auto-activating components: drop `.example` to enable.

## Permissions / settings

`.claude/settings.json.example` shows a project/plugin `settings.json` with a
`permissions` block: `allow` runs a tool silently, `ask` prompts the user, and
`deny` refuses outright (deny wins over allow on a conflict). It also enables the
plugin via `enabledPlugins`. Rename it to `.claude/settings.json` to take
effect — Claude does not read `.example` files.

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
