# Component: Monitors  *(experimental)*

> A long-running background process whose output becomes notifications.

## What it is

A monitor is a **background process** that keeps running; its output lines become
notifications. Real monitors watch logs or a deployment, for example.

## File & format

- **Config:** `example/monitors/monitors.json` (here `.example`).
- **Program:** usually a `.sh` in `monitors/scripts/` that runs continuously.
- **Config format:** `.json` — a list of monitor entries.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When does it run? | At **session start** (interactive sessions) — or only on an event, e.g. `when: "on-skill-invoke:run-greet"`. |
| Who triggers it? | **Automatic** on load (or the named event). |
| Where does it run? | As a persistent **background process**. |

Because it is a long-running process, the example ships it defused as `.example`.

## Status

**Experimental** (Claude Code v2.1.105+). Use carefully in public plugins.

## In the example plugin (PR #1)

`monitors/monitors.json.example` + `monitors/scripts/heartbeat.sh` — the example
monitor prints a "heartbeat" line every 30 seconds.
