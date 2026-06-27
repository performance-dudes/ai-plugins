# Component: Workflow technique (`greet.js`)

> A small multi-step script (an "assembly line"). Not an auto-loaded component — a
> **technique**.

## What it is

A workflow is a small program that runs in steps. Here it takes a name, asks a
small model for a greeting, and returns a result.

## Important: a technique, not an auto-component

Unlike a command/skill/agent, a workflow script is **not** auto-discovered. The
plugin keeps the script in `workflows/` and calls it **by path** from a command or
a skill:

```js
Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/greet.js", args: "$ARGUMENTS" })
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's install directory, so the script
is found no matter where the plugin is installed.

## File & format

- **File:** `example/workflows/<name>.js`.
- **Format:** `.js` (JavaScript) — executed by the workflow engine.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When does it run? | Only when a command or skill starts it **by `scriptPath`**. |
| Who triggers it? | A command or a skill. |
| Where does it run? | In the background; it returns a result (`{ who, greeting }`). |

## In the example plugin (PR #1)

`workflows/greet.js` reads `args` (the name), calls a small fast model, and returns
`{ who, greeting }`. The command **and** the skill both use this one script — a
single source of truth.
