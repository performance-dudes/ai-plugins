# Understanding the `example` plugin — documentation

This `docs/` folder explains the `example` plugin (#1) **from zero**, so that
someone who has never seen a Claude Code plugin can understand one.

> `docs/` = what **is** (current state). `specs/` = what **should be** (intent).
> `journal/` = what we **did and learned**. The running plugin stays in `example/`.

## Map (filled in this PR)

| Page | What it gives you |
|------|-------------------|
| `file-formats.md` | Why `.json` / `.md` / `.sh` — the key to the architecture. |
| `architecture.md` | What is read when, who triggers it, where it runs. |
| `components/` | One page per component (manifest, command, skill, subagent, workflow, theme, output-style, hooks, mcp, lsp, monitors). |

## Tested

Everything is validated by `tests/run-all.sh` (every config is valid JSON, the
workflow is valid JS, every script runs). It does **not** activate the defused
`.example` components — it only checks them.
