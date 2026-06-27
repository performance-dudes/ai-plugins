# PD-conformant reference for the example plugin — 2026-06-27

**What** — Adds a PD-conformant **reference spec** for the `example` plugin
(`specs/example/0001_product_example.md`) plus this journal entry. The `example`
plugin itself lives in `plugins/example/` and is validated by its own
`plugins/example/tests/validate.sh` (every component file present, every JSON
valid, every script runnable). Goal: a newcomer can learn every plugin component
type from one working, provably-healthy example.

**How / decisions**
- Followed `craft/spec-driven-tdd`: spec first, PR opened early, then filled.
- Each component self-documents inside `plugins/example/`, **separate** from a
  `docs/` page — because every `.md` inside `commands/` or `agents/` is loaded as a
  real command/agent, so docs placed there would create bogus commands and break
  the showcase.
- The `.example` configs (mcp/lsp/hooks/monitors) are **validated, not activated**:
  deliberately defused; activating them would auto-run components that need
  external servers. The test runner validates them without switching them on.

**Learnings**
- The PD way was not obvious at first: a first attempt produced many tiny PRs and
  an ad-hoc layout. The correction: **the internal plugins `craft` + `knowledge`
  hold the rules** (`spec-driven-tdd`, `docs`, `journal`). They were installed but
  **disabled** — `plugin-hygiene` says enable per project (`.claude/settings.local.json`
  here, to keep the public repo clean), then `/reload-plugins`.
- Takeaway for next time: **before starting, check whether a PD plugin/skill covers
  the task and load it** — don't invent a process.
- Rebase learning: while this PR was open, the repo convention landed centrally
  (#41 foundation, #42 `plugins/` move). Rebasing onto the new `main` turned the
  scaffold files this PR had started (`docs/README.md`, `journal/README.md`,
  `tests/run-all.sh`) into duplicates — they were dropped, so the PR's real value is
  only the reference spec. And: **an AC is green only when a real test measures it**,
  so the ACs now point at `plugins/example/tests/validate.sh`, not the generic runner.
