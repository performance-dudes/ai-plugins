# Spec: `settings.json` component  *(documentation of a gap)*

**Theme:** The reference explains plugin-level settings (and the subagent status
line), even though the example plugin does not ship them yet.

## US-SETTINGS-1 — Understand plugin settings and the status line

> As a **reader**, I want to understand plugin-level `settings.json` and the
> subagent status line, so that I could configure them in my own plugin.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-SETTINGS-1-1 | The page documents `settings.json` and its supported keys. | `test.sh` (grep `settings.json`) |
| AC-SETTINGS-1-2 | The page documents `subagentStatusLine` (the status line). | `test.sh` (grep `subagentStatusLine`) |
| AC-SETTINGS-1-3 | The page clearly marks this as a gap (not shipped yet). | `test.sh` (grep `gap`) |
