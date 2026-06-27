# Spec: `bin/` executables component  *(documentation of a gap)*

**Theme:** The reference explains how a plugin exposes executables on PATH, even
though the example plugin does not ship one yet.

## US-BIN-1 — Understand bundled executables

> As a **reader**, I want to understand how a plugin puts executables on PATH, so
> that I could add one to my own plugin.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-BIN-1-1 | The page explains the PATH behaviour. | `test.sh` (grep `PATH`) |
| AC-BIN-1-2 | The page documents the file & format (executable). | `test.sh` (grep `executable`) |
| AC-BIN-1-3 | The page clearly marks this as a gap (not shipped yet). | `test.sh` (grep `gap`) |
