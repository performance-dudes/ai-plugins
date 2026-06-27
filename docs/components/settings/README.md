# Component: `settings.json` (plugin defaults & status line)  *(not shipped in the example yet)*

> Default configuration a plugin applies when it is enabled — including the
> subagent **status line**.

## What it is

A plugin can ship a `settings.json` at its root. When the plugin is enabled, these
defaults are applied. Only two keys are supported: **`agent`** and
**`subagentStatusLine`**.

## The "statusline" lives here

`subagentStatusLine` customises the little status line shown for subagents — this
is the "statusline" feature. It is **not** a separate component; it is a key inside
`settings.json`.

## File & format

- **File:** `settings.json` (at the plugin root).
- **Format:** `.json` — data read by Claude Code.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | At **session start**, applied when the plugin is enabled. |
| Who triggers it? | **Automatic** on load. |
| Where does it run? | Nowhere — it is **data only**. |

## Status in the example plugin

**Not shipped yet — this is a gap.** The example plugin from #1 has no
`settings.json`.

## How you would add it

```json
// example/settings.json
{
  "subagentStatusLine": { "type": "command", "command": "echo subagent running" }
}
```
