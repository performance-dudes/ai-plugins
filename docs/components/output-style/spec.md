# Spec: Output-style component

**Theme:** The plugin ships an opt-in output style that changes how Claude answers.

## US-OUTPUTSTYLE-1 — An opt-in terse style

> As a **user**, I want to switch to a terse answer style, so that responses are
> short and direct.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-OUTPUTSTYLE-1-1 | The style file exists at `example/output-styles/terse.md`. | `test.sh` (file presence) |
| AC-OUTPUTSTYLE-1-2 | Its frontmatter has `name` and `description`. | `test.sh` (grep) |
