# Spec: PD reference for the `example` plugin

**Theme:** Make the `example` plugin the complete, beginner-friendly, **tested**
reference for building Claude Code plugins the PD way — one real, minimal file per
component type, every file validated and every script runnable — so that anyone,
even without prior exposure to Claude Code, can learn plugin-building from a working,
provably-healthy example.

Hierarchy: **theme → user story (US) → acceptance criteria (AC) + test reference.**
Built following the PD plugin house style and the internal skills
`craft/spec-driven-tdd` and `knowledge/docs`.

---

## US-REF-1 — One real file per component type
> As a **newcomer**, I want one real, minimal file per plugin component, so that I
> can study each component type on its own from a working example.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-REF-1-1 | `plugins/example/` has one real file per component type: command (`commands/greet.md`), skill (`skills/run-greet/SKILL.md`), subagent (`agents/greeter.md`), workflow (`workflows/greet.js`), theme (`themes/performance-dudes.json`), output-style (`output-styles/terse.md`), hooks (`hooks/scripts/*.sh`). | `plugins/example/tests/validate.sh` (component files present) |
| AC-REF-1-2 | Skill and subagent self-document via frontmatter `name` + `description`. | `plugins/example/tests/validate.sh` (frontmatter check) |

## US-REF-2 — Every plugin file valid, every script runnable
> As a **developer**, I want every file in the plugin validated and every script
> runnable, so that the showcase is provably healthy.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-REF-2-1 | Manifest + marketplace validate; every JSON / `.json.example` file parses as valid JSON. | `plugins/example/tests/validate.sh` |
| AC-REF-2-2 | The workflow script is valid JavaScript (`node --check`). | `plugins/example/tests/validate.sh` |
| AC-REF-2-3 | Every hook shell script has valid syntax (`bash -n`). | `plugins/example/tests/validate.sh` |

## US-REF-3 — Clean PD-conformant structure
> As a **teammate**, I want the work split into `specs/` (intent), `docs/` (state)
> and `journal/` (logbook), so that it follows the PD standard.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-REF-3-1 | Top-level `specs/`, `docs/`, `journal/`, `tests/` exist. | `tests/run-all.sh` (structure check) |
| AC-REF-3-2 | This spec follows the naming scheme `NNNN_type_plugin` (`specs/example/0001_product_example.md`) and a journal entry records the work. | structure check (enforces naming) + review |
