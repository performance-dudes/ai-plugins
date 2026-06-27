# Spec: Monitors component  *(experimental)*

**Theme:** The plugin ships a defused background-monitor template.

## US-MONITORS-1 — A defused monitor template

> As a **plugin author**, I want a defused monitor template, so that I can see how a
> background process is wired without it auto-running.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-MONITORS-1-1 | The template exists at `example/monitors/monitors.json.example`. | `test.sh` (file presence) |
| AC-MONITORS-1-2 | It is valid JSON. | `test.sh` (`python3 -m json.tool`) |
| AC-MONITORS-1-3 | The monitor script exists and has a shebang. | `test.sh` (grep `#!`) |
