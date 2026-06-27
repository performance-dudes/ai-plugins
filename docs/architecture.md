# Architecture: what is read when, who triggers it, where it runs

Every plugin building block is read or run at a specific moment. There are **three
sorts**, by who triggers them:

| Sort | Components | Trigger |
|------|-----------|---------|
| **You type something** | command, theme, output-style | you |
| **Claude decides** | skill, subagent | the model |
| **Runs automatically on load** | hooks, MCP, LSP, monitors | the program → shipped as `.example` |

## When is each read, and where does it run?

| Component | When read | Who triggers | Where it runs |
|-----------|-----------|--------------|---------------|
| Manifest | session start | Claude Code | — (data only) |
| Marketplace | when you add the marketplace | you | — (data only) |
| Command | session start; runs on `/greet` | you | Claude follows the `.md` |
| Skill | session start; runs on match | Claude | Claude follows the `SKILL.md` |
| Subagent | session start; on `subagent_type` | Claude | a separate agent |
| Workflow | only when called by `scriptPath` | command/skill | the workflow engine |
| Theme / Output-style | session start; active on `/theme` · `/output-style` | you | interface / answer style |
| Hooks / MCP / LSP / Monitors | **session start, automatically** | the program | executed immediately → `.example` |

## The rule of thumb

Blocks **you** or **Claude** trigger are safe — nothing runs unasked. The
**automatic** ones (hooks, MCP, LSP, monitors) start at load, which is why the
example ships them defused as `.example`.

## Where does an installed plugin live?

After `claude plugin install`, the plugin is cached at
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. The variable
`${CLAUDE_PLUGIN_ROOT}` points to exactly that folder — which is why a command can
find its bundled script "no matter where" the plugin is installed.
