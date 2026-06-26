# example — plugin-bundled dynamic Workflow

A minimal, copy-me reference showing how a Claude Code plugin can **ship a
dynamic Workflow** and expose it through a slash command.

## Why this exists

Named-workflow resolution (`Workflow({ name })`) only knows built-ins and the
files present in `~/.claude/workflows/` / `.claude/workflows/` **at session
start** — it does not discover plugin scripts, and it is not live-scanned.

The working pattern (used by Anthropic's official `code-modernization` plugin)
is to ship the script in `workflows/` and invoke it **by path** from a command:

```js
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/greet.js",
  args: "$ARGUMENTS"
})
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's install directory, so the same
command works no matter where the plugin was installed.

## Layout

```
example/
├── .claude-plugin/plugin.json
├── workflows/greet.js     # export const meta + agent()/phase()/log()
└── commands/greet.md      # /greet — invokes the workflow via scriptPath
```

## Usage

After enabling the plugin, run:

```
/greet Felix
```

The command runs `workflows/greet.js`, which spawns one agent and returns
`{ who, greeting }`.
