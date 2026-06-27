# Component: Theme  *(experimental)*

> A color scheme for the Claude Code interface.

## What it is

A theme changes the **colors** of the Claude Code interface.

## File & format

- **File:** `example/themes/<name>.json` (here `themes/performance-dudes.json`).
- **Format:** `.json` — a program reads **exact color values**, so it is data, not
  prose (that is why it is not a `.md`).

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | Discovered at **session start**. |
| When is it active? | Only when you opt in with `/theme`. |
| Who triggers it? | **You** — nothing changes unasked. |

## Status

**Experimental.** For a public plugin used by a broad audience, apply it with care;
internally it is fine.

## In the example plugin (PR #1)

`themes/performance-dudes.json` shows the shape of a theme: a base scheme plus a
few overridden colors.
