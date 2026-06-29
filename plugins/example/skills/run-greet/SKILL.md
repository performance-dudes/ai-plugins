---
name: run-greet
description: Greet someone using the plugin's bundled greet workflow. Use when the user asks to greet a person/team, wants a friendly one-line greeting, or asks to run/demo the example greet workflow.
argument-hint: "[name]"
---

# run-greet — call the bundled workflow from a skill

This skill demonstrates the cleanest way for a **skill** to invoke a
**dynamic workflow** that ships in the same plugin.

## What to do

1. Determine the name to greet from the user's request (default: `world`).

2. If the **Workflow tool is available**, run the bundled script. `${CLAUDE_PLUGIN_ROOT}`
   resolves to this plugin's install directory, so `workflows/greet.js` is found
   regardless of where the plugin was installed:

   ```
   Workflow({
     scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/greet.js",
     args: "<name>"
   })
   ```

   The workflow runs in the background and returns `{ who, greeting }`. Report the
   `greeting` to the user when the task-notification arrives.

3. If the **Workflow tool is NOT available** (e.g. a constrained session), fall
   back to greeting the name yourself in one friendly line — same outcome, no
   orchestration.

## Why a skill *and* a command?

- `commands/greet.md` is the explicit `/greet` entry point a user types.
- This skill lets the model invoke the same workflow *autonomously* when a
  request matches its `description`, without the user remembering a command.

Both funnel into the one workflow script — single source of truth.
