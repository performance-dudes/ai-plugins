# Understanding a Claude Code plugin — by example

Welcome. This repository ships the **`example` plugin** (introduced in #1): a
copy-me reference that shows **every** Claude Code plugin component. This `docs/`
folder explains all of it **from zero**, so that someone who has never seen a
plugin can understand one.

## Start here

| Page | What it gives you |
|------|-------------------|
| [file-formats.md](file-formats.md) | Why some files are `.json`, some `.md`, some `.sh` — the key to the whole architecture. |
| [architecture.md](architecture.md) | The big picture: **what is read when, who triggers it, and where it runs**. |
| [components/](components/README.md) | **One page per component**: what it is, its file & format, its architecture, the real file in the example plugin, and a test. |

## What is a plugin, in one line?

A plugin is a **folder of building blocks** that Claude Code loads to gain new
abilities. Each block is read or run at a specific moment; several blocks can work
together (in the example, a command, a skill and a workflow all produce one
greeting).

## How this documentation is organised

- `docs/` describes **what is** (the current state).
- `docs/components/<name>/` holds, per component, a `README.md` (docs), a
  `spec.md` (intent), and a `test.sh` (a runnable check).
- The live plugin stays in `example/` and is never mixed with these docs — see
  [components/README.md](components/README.md) for why.
