---
description: Check that the context-aware plugin's dependencies are present (node, the context-mode MCP enabled at the workspace level, claude CLI)
---

# /context-aware-doctor — preflight check

Verify the local environment can run the context-aware demo. Run the bundled
check and present the result as a checklist, with the exact fix command for
anything missing. **Do not install anything automatically** — show the command
and let the user run it.

!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/doctor.sh`

Each line is `OK`, `MISS` (needs a fix) or `----` (optional). Summarize what is
ready and what to install, grouped by tier:

- **required** — `claude` CLI, `node >= 20` (the Workflow tool needs node;
  without it the command still works via the Bash fallback, but the orchestration
  demo does not run), and the **context-mode** plugin — the `ctx_*` retrieval
  substrate. This plugin does **not** bundle context-mode; it is enabled **once at
  the workspace level** (`claude plugin marketplace add mksglu/context-mode` →
  `claude plugin install context-mode@context-mode`). Without it the `ctx_*` tools
  are absent and the agents degrade to reading reference files directly.

Close with a one-line verdict: **ready**, or **blocked** with the required item
that is missing.
