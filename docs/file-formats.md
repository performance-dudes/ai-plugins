# File formats: why `.json`, `.md`, `.sh`, `.yml`?

A file's extension tells you **who reads it and how**. This is the key to the
whole plugin architecture.

| Extension | What it is | Who reads / runs it | Examples |
|-----------|-----------|---------------------|----------|
| `.json` | strict **data** (keys → values) | a **program** reads it as config | `plugin.json`, `marketplace.json`, `themes/*.json`, `.mcp.json` |
| `.md` | **text / instructions** in plain language | the **model (Claude)** reads and follows it | `commands/greet.md`, `SKILL.md`, `agents/greeter.md` |
| `.sh` | an **executable program** (shell commands) | the **operating system** runs it | `hooks/scripts/*.sh`, `tests/validate.sh` |
| `.yml` | data like JSON, friendlier to read | here: **GitHub** for the automatic check | `.github/workflows/validate.yml` |
| `.js` | a **JavaScript** program | the **workflow engine** runs it | `workflows/greet.js` |
| `.example` | not a format — an **off switch** | nobody, until you remove the suffix | `hooks.json.example` |

## The one big rule

> `.json` / `.yml` → a **program** reads **data**.
> `.md` → the **model** reads **instructions**.
> `.sh` / `.js` → something gets **executed**.

That is why a command is a `.md` (Claude reads your instruction in words) but a
theme is a `.json` (the program needs exact colour values). **The format follows
the job.**

## What is frontmatter?

Many `.md` files start with a block between `---` lines:

```markdown
---
name: greeter
description: ...
---
(plain instruction text for the model from here on)
```

The `---` block holds the few **machine-readable fields** (name, description). The
text below is the **instruction** for the model. So one `.md` file carries a little
data on top and instructions below.
