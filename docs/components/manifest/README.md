# Component: Manifest (`plugin.json`)

> The plugin's ID card. Without it (at the default location) a folder is not a
> real plugin.

## What it is

The manifest is a small data file that tells Claude Code the plugin's **name**,
**version** and **description**. It is the first thing read when the plugin loads.

## File & format

- **File:** `example/.claude-plugin/plugin.json`
- **Format:** `.json` — a strict data format (keys → values). A **program**
  (Claude Code) reads it, so there is no prose, only exact fields.

## Architecture: when is it read, who triggers it, where does it run?

| Question | Answer |
|----------|--------|
| When is it read? | At **session start**, when the plugin is loaded. |
| Who triggers it? | Claude Code itself — automatically. |
| Where does it "run"? | Nowhere — it is **data only**, not a program. It is just read. |

## Fields

- **Required:** `name` (kebab-case, e.g. `my-plugin`). Used to namespace the
  plugin's skills/commands (e.g. `/my-plugin:greet`).
- **Optional:** `description`, `version`, `author`, `homepage`, `repository`,
  `license`, `keywords`, `displayName`.
- If you omit `version`, the current git commit is used instead.

## In the example plugin

`example/.claude-plugin/plugin.json` is intentionally minimal: `name`,
`description`, `version`, `author`, `keywords`. That is the smallest sensible
manifest — copy it as your starting point.

## Pro tip

Add a `$schema` line so your editor autocompletes and validates fields while you
type:

```json
{ "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json" }
```
