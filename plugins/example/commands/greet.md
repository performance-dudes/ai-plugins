---
description: Run the bundled greet workflow for a given name
argument-hint: "[name]"
---

Run the plugin's bundled dynamic workflow.

**Preferred — Workflow orchestration.** If the **Workflow tool** is available,
invoke the bundled script directly. `${CLAUDE_PLUGIN_ROOT}` resolves to this
plugin's install directory regardless of where it was installed:

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/greet.js",
  args: "$ARGUMENTS"
})
```

When it completes, report the returned `greeting` to the user.

**Fallback (no Workflow tool).** Greet `$ARGUMENTS` yourself in one friendly line.
