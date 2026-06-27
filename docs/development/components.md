# Die Bausteine einzeln erklärt

Jeder Plugin-Baustein hat eine Aufgabe und wird zu einem bestimmten Moment aktiv.
Es gibt **drei Sorten**, je nachdem, *wer* sie auslöst:

- **Du tippst etwas** → Command, Theme, Output-Style.
- **Claude entscheidet selbst** → Skill.
- **Läuft automatisch beim Laden** → Hooks, MCP, LSP, Monitore. Genau die sind
  als `.example`-Vorlagen entschärft, damit nichts ungefragt losläuft.

## Übersicht

| Baustein | Datei | Was es ist | Wer löst es aus |
|----------|-------|------------|-----------------|
| Manifest | `.claude-plugin/plugin.json` | der Steckbrief (Name, Version) | Claude beim Laden |
| Workflow | `workflows/greet.js` | kleines Programm in mehreren Schritten | Command/Skill |
| Command | `commands/greet.md` | ein Befehl zum Tippen: `/greet` | du |
| Skill | `skills/run-greet/SKILL.md` | Fähigkeit, die Claude selbst startet | Claude |
| Subagent | `agents/greeter.md` | ein Helfer mit eigenen Rechten (nur Muster) | per Aufruf |
| Theme | `themes/performance-dudes.json` | Farbschema | du (`/theme`) |
| Output-Style | `output-styles/terse.md` | ändert *wie* Claude antwortet | du (`/output-style`) |
| Hook | `hooks/…` | Programm, das automatisch mitläuft | automatisch (`.example`) |
| MCP | `.mcp.json.example` | Anbindung an einen externen Server | automatisch (`.example`) |
| LSP | `.lsp.json.example` | Anbindung an ein Sprach-Werkzeug | automatisch (`.example`) |
| Monitor | `monitors/…` | Hintergrund-Prozess | automatisch (`.example`) |

## Kurz erklärt

- **Manifest** — die Visitenkarte des Plugins. Ohne sie ist es kein Plugin.
- **Workflow** — das einzige echte „Programm" hier. Nimmt einen Namen, fragt ein
  Modell, gibt ein Ergebnis zurück.
- **Command** — ein Zettel mit einer Anweisung, der bei `/greet` gelesen wird.
- **Skill** — wie ein Command, aber Claude wählt ihn **selbst**, wenn die Anfrage
  passt. Gleicher Workflow dahinter.
- **Subagent** — ein Spezial-Helfer mit eng begrenzten Rechten. Hier nur als
  Vorlage dabei.
- **Theme / Output-Style** — Aussehen bzw. Antwort-Stil. Freiwillig einschaltbar.
- **Hook / MCP / LSP / Monitor** — laufen automatisch mit, sobald sie scharf sind.
  Deshalb liegen sie hier nur als entschärfte `.example`-Vorlagen.

## Warum manche `.example` heißen

Bausteine, die du selbst startest, sind ungefährlich — es passiert nichts, bis du
sie aufrufst. Die automatischen (Hook, MCP, LSP, Monitor) würden aber sofort beim
Laden loslaufen und brauchen oft ein extra Programm. Damit das Beispiel **gefahrlos**
bleibt, liegen sie als `.example` da. Zum Ausprobieren entfernt man die Endung.
