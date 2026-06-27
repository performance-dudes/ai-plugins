# Spec: Manifest component

**Theme:** The example plugin ships a valid, minimal manifest that identifies the
plugin to Claude Code.

Hierarchy: **theme → user story (US) → acceptance criteria (AC) + test reference.**

## US-MANIFEST-1 — A valid, minimal manifest

> As a **plugin author**, I want a minimal, valid `plugin.json` to copy, so that
> my own plugin is recognised by Claude Code.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-MANIFEST-1-1 | The manifest file exists at `example/.claude-plugin/plugin.json`. | `test.sh` (file presence) |
| AC-MANIFEST-1-2 | The manifest is valid JSON. | `test.sh` (`python3 -m json.tool`) |
| AC-MANIFEST-1-3 | The manifest declares the required `name` field. | `test.sh` (grep `"name"`) |
