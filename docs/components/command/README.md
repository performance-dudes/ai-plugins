# Component: Slash command (`/greet`)

> A command you type. Claude reads the matching `.md` file and follows it.

## What it is

A slash command is an **instruction sheet**. When you type `/greet`, Claude reads
`commands/greet.md` and does what it says. You trigger it on purpose.

## File & format

- **File:** `example/commands/<name>.md` (here `commands/greet.md`).
- **Format:** `.md` — the **model** reads instructions in plain language. The top
  is frontmatter (`description`, `argument-hint`); below is the instruction text.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | Discovered at **session start** (reloaded on `/reload-plugins`). |
| Who triggers it? | **You** — by typing `/greet`. |
| Where does it run? | Claude follows the markdown; here it starts the bundled workflow. |

## In the example plugin (PR #1)

`commands/greet.md` tells Claude to run `workflows/greet.js` by `scriptPath` and
pass `$ARGUMENTS` — the text after the command. `/greet Felix` → `$ARGUMENTS` is
`Felix`.

## Important caveat

**Every `.md` in `commands/` becomes a command.** A `commands/README.md` would
create a bogus `/readme` command. That is exactly why this documentation lives in
`docs/` and not inside the plugin's `commands/` folder.
