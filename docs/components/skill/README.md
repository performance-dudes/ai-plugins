# Component: Skill (`run-greet`)

> A capability Claude starts **on its own** when your request matches it.

## What it is

A skill lets Claude act **without you typing a command**. Claude reads each skill's
`description` and decides, on its own, when the skill applies to your request.

## File & format

- **File:** `example/skills/<name>/SKILL.md` (here `skills/run-greet/SKILL.md`).
  Each skill lives in its **own subfolder**.
- **Format:** `.md` with frontmatter (`name`, `description`) + instruction text.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | Discovered at **session start**; the `description` is matched continuously. |
| Who triggers it? | **Claude** — automatically, when your request matches the `description`. |
| Where does it run? | Claude follows the `SKILL.md`; here it runs the same workflow as the command. |

## Command vs. skill

- **Command:** you type `/greet`.
- **Skill:** you say *"greet the team"* and Claude starts it for you.

Both funnel into the **same workflow** → one source of truth.

## In the example plugin (PR #1)

`skills/run-greet/SKILL.md` calls the same `workflows/greet.js` as the command.

## Note

Inside a skill's **own** subfolder you may safely add helper files (references,
scripts). Only the `SKILL.md` itself is loaded as the skill.
