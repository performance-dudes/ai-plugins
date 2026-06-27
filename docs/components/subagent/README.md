# Component: Subagent (`greeter`)

> A specialized helper with its own, **limited** permissions.

## What it is

A subagent is a focused helper Claude can hand a task to. It does the work and
returns **just a result**. It has its own allow-list of tools — only what it needs.

## File & format

- **File:** `example/agents/<name>.md` (here `agents/greeter.md`).
- **Format:** `.md` with frontmatter (`name`, `description`, `model`, `tools`) +
  instruction text.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | Discovered at **session start**. |
| Who triggers it? | **Claude** (or a workflow), via `subagent_type: "greeter"`. |
| Where does it run? | As a **separate agent** with its own limited tools. |

## In the example plugin (PR #1)

`agents/greeter.md` is a **template** ("what an agent file looks like"). The
`/greet` flow does **not** use it — it calls a small model directly. The template
only shows the shape.

## Least privilege

`tools: [Read]` gives the helper **only** reading — no writing, no executing. Fewer
rights = less can go wrong. This is a security principle.

## Important caveat

**Every `.md` in `agents/` becomes an agent** — so this documentation lives in
`docs/`, not inside the plugin's `agents/` folder.
