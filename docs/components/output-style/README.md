# Component: Output style (`Terse`)

> Changes **how** Claude answers (not *what* it answers).

## What it is

An output style changes the **manner** of Claude's answers. The example one says:
"be as short as correctness allows, no filler."

## File & format

- **File:** `example/output-styles/<name>.md` (here `output-styles/terse.md`).
- **Format:** `.md` with frontmatter (`name`, `description`) + instruction text.
  The text is **appended to Claude's system prompt** while the style is active.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | Discovered at **session start**. |
| When is it active? | After you run `/output-style Terse`. |
| Who triggers it? | **You** — opt-in. |

## In the example plugin (PR #1)

`output-styles/terse.md` is a concise answer style. Try it with
`/output-style Terse`.
