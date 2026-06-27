# Spec: Command component

**Theme:** Typing `/greet <name>` runs the plugin's bundled workflow.

## US-COMMAND-1 — Greet via the `/greet` command

> As a **user**, I want to type `/greet <name>` and have the bundled workflow run,
> so that I get a short greeting.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-COMMAND-1-1 | The command file exists at `example/commands/greet.md`. | `test.sh` (file presence) |
| AC-COMMAND-1-2 | It has a `description` in its frontmatter. | `test.sh` (grep `description:`) |
| AC-COMMAND-1-3 | It invokes the bundled workflow by path. | `test.sh` (grep `greet.js`) |
