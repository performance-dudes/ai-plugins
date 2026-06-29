# PD-conformant reference for the example plugin — 2026-06-27

**What** — Adds a complete, tested reference for the `example` plugin (#1), in one
PR with a clean PD structure: `specs/` (intent), `docs/` (one page per component),
`journal/` (this logbook), and `tests/run-all.sh` (validates every plugin file and
runs every script). Goal: a newcomer can understand every plugin component on its
own, and the showcase is provably healthy.

**How / decisions**
- Followed `craft/spec-driven-tdd`: spec first, PR opened early, then filled.
- Documentation lives in `docs/`, **separate** from the running plugin in
  `example/` — because every `.md` inside `commands/` or `agents/` is loaded as a
  real command/agent, so docs placed there would create bogus commands and break
  the showcase.
- The `.example` configs (mcp/lsp/hooks/monitors) are **validated, not activated**:
  they are deliberately defused, and activating them would auto-run components that
  need external servers. The test runner validates them without switching them on.

**Learnings**
- The PD way was not obvious at first: a first attempt produced many tiny PRs and
  an ad-hoc layout. The correction: **the internal plugins `craft` + `knowledge`
  hold the rules** (`spec-driven-tdd`, `docs`, `journal`). They were installed but
  **disabled** — `plugin-hygiene` says enable per project (`.claude/settings.local.json`
  here, to keep the public repo clean), then `/reload-plugins`.
- Takeaway for next time: **before starting, check whether a PD plugin/skill covers
  the task and load it** — don't invent a process.

**Follow-ups**
- Fill `docs/components/<name>.md` for every component (in this same PR).
- Optionally add the missing components (`bin/`, `settings.json`) to the plugin.
