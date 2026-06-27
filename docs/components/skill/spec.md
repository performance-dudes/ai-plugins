# Spec: Skill component

**Theme:** Claude can greet someone autonomously (without a typed command) by
triggering the `run-greet` skill, which runs the same bundled workflow.

## US-SKILL-1 — Greet without a command

> As a **user**, I want a friendly greeting even when I phrase a normal request, so
> that Claude triggers the skill on its own.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-SKILL-1-1 | The skill exists at `example/skills/run-greet/SKILL.md`. | `test.sh` (file presence) |
| AC-SKILL-1-2 | Its frontmatter has `name` and `description`. | `test.sh` (grep) |
| AC-SKILL-1-3 | It calls the bundled workflow. | `test.sh` (grep `greet.js`) |
