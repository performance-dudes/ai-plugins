# Spec: PD-conformant reference for the `example` plugin

**Theme:** Provide a complete, beginner-friendly, **tested** reference for the
`example` plugin, so that anyone — even without prior exposure to Claude Code —
can understand every component, and so that every plugin file is validated and
every script is runnable.

Hierarchy: **theme → user story (US) → acceptance criteria (AC) + test reference.**
Built following the internal skills `craft/spec-driven-tdd` and `knowledge/docs`.

---

## US-REF-1 — One documentation page per component
> As a **newcomer**, I want one page per plugin component, so that I can
> understand each one on its own.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-REF-1-1 | `docs/components/` has one page per component (manifest, marketplace, command, skill, subagent, workflow, theme, output-style, hooks, mcp, lsp, monitors). | `tests/run-all.sh` (structure check) |
| AC-REF-1-2 | Each page explains: what it is, file & format, and the architecture (when read / who triggers / where it runs). | review |

## US-REF-2 — Every plugin file valid, every script runnable
> As a **developer**, I want every file in the plugin validated and every script
> runnable, so that the showcase is provably healthy.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-REF-2-1 | Every JSON / `.json.example` file parses as valid JSON. | `tests/run-all.sh` |
| AC-REF-2-2 | The workflow script is valid JavaScript (`node --check`). | `tests/run-all.sh` |
| AC-REF-2-3 | Every shell script has valid syntax and is executable; the hook runs in isolation and exits 0. | `tests/run-all.sh` |

## US-REF-3 — Clean PD-conformant structure
> As a **teammate**, I want the work split into `specs/` (intent), `docs/` (state)
> and `journal/` (logbook), so that it follows the PD standard.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-REF-3-1 | `specs/`, `docs/`, `journal/`, `tests/` exist with the expected content. | `tests/run-all.sh` (structure check) |
| AC-REF-3-2 | A journal entry records this work and its learnings. | review |
