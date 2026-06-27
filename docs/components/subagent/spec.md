# Spec: Subagent component

**Theme:** The plugin ships a minimal subagent template with least-privilege tools.

## US-SUBAGENT-1 — A minimal subagent template

> As a **plugin author**, I want a minimal subagent template, so that I can model
> my own agents on it.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-SUBAGENT-1-1 | The agent file exists at `example/agents/greeter.md`. | `test.sh` (file presence) |
| AC-SUBAGENT-1-2 | Its frontmatter has `name` and `description`. | `test.sh` (grep) |
| AC-SUBAGENT-1-3 | It declares a `tools` allow-list (least privilege). | `test.sh` (grep `tools:`) |
