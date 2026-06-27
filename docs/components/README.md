# Die Plugin-Bausteine — vollständige Referenz

Ein Plugin ist ein **Ordner voller Bausteine**. Jeder Baustein hat eine Aufgabe und
wird zu einem bestimmten Moment **gelesen** oder **ausgeführt**. Hier ist jeder
Baustein einzeln erklärt — nach dem gleichen Muster: *Was? · Datei & Format ·
Wann/von wo gelesen, wo ausgeführt · im example-Plugin*.

## Die drei Sorten (wer löst den Baustein aus?)

| Sorte | Bausteine | Auslöser |
|---|---|---|
| **Du tippst etwas** | Command, Theme, Output-Style | du |
| **Claude entscheidet selbst** | Skill, Subagent | das Modell |
| **Läuft automatisch beim Laden** | Hooks, MCP, LSP, Monitors | das Programm → deshalb als `.example` entschärft |

## Alle Bausteine

| Seite | Baustein | Status |
|---|---|---|
| [manifest.md](manifest.md) | Manifest (`plugin.json`) | offiziell |
| [marketplace.md](marketplace.md) | Marketplace (`marketplace.json`) | offiziell |
| [command.md](command.md) | Slash-Command | offiziell |
| [skill.md](skill.md) | Skill | offiziell |
| [subagent.md](subagent.md) | Subagent | offiziell |
| [workflow.md](workflow.md) | Workflow-Technik (Script per Pfad) | Technik, kein Auto-Baustein |
| [theme.md](theme.md) | Theme | experimentell |
| [output-style.md](output-style.md) | Output-Style | offiziell |
| [hooks.md](hooks.md) | Hooks (24+ Event-Typen) | offiziell |
| [mcp.md](mcp.md) | MCP-Server | offiziell |
| [lsp.md](lsp.md) | LSP-Server | offiziell |
| [monitors.md](monitors.md) | Monitors | experimentell |

## Im example-Plugin noch nicht gezeigt (Lücken)

- `bin/` — mitgelieferte ausführbare Programme, die in den PATH kommen.
- `settings.json` — Plugin-Standardeinstellungen (nur `agent` + `subagentStatusLine`).

Diese beiden fehlen noch — siehe Issue #3.

## Wo wird ein installiertes Plugin überhaupt gelesen?

Nach `claude plugin install` liegt das Plugin im **Cache**:
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`.
Der Platzhalter `${CLAUDE_PLUGIN_ROOT}` zeigt genau auf diesen Ordner — deshalb
findet ein Command sein Script „egal wo".
