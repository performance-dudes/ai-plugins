# Spec: `example`-Plugin — Referenz-Showcase

**Thema (ein Spec = ein Thema):** Das `example`-Plugin ist eine kopierbare
Referenz, die *jeden* Claude-Code-Plugin-Baustein einmal vorzeigt und zugleich
zeigt, *wie* man Plugins und Skills testet.

Hierarchie dieser Spec: **Thema → User Story (US) → Acceptance Criterion (AC) +
Test-Referenz.** Jedes AC hängt unter genau einer US und zeigt auf einen Test.

---

## US-001-1 — Jeder Baustein als kopierbare Vorlage
> Als **Plugin-Einsteiger** will ich von jedem Baustein-Typ eine kopierbare
> Vorlage im Plugin finden, damit ich mein eigenes Plugin daraus ableiten kann.

| AC | Kriterium | Test-Referenz |
|----|-----------|---------------|
| AC-001-1-1 | Für jeden aktiven Baustein (Manifest, Workflow, Command, Skill, Subagent, Theme, Output-Style) liegt genau eine Beispieldatei vor. | `tests/validate.sh` Schritt 2 (Component files present) |
| AC-001-1-2 | Alle JSON-Bausteine sind gültiges JSON. | `tests/validate.sh` Schritt 1 + 3 |
| AC-001-1-3 | Das Workflow-Skript ist syntaktisch gültiges JavaScript. | `tests/validate.sh` Schritt 4 (`node --check`) |
| AC-001-1-4 | Skill und Subagent tragen `name` + `description` im Frontmatter. | `tests/validate.sh` Schritt 5 |
| AC-001-1-5 | Auto-aktive Bausteine (Hooks, MCP, LSP, Monitore) werden entschärft als `.example` ausgeliefert. | informativ (Dateiendung `.example` vorhanden) |

---

## US-001-2 — Wissen, wie man Plugins/Skills testet
> Als **Entwickler** will ich dokumentiert haben, wie ich Plugins und Skills
> teste, damit ich meine Änderungen absichern kann.

| AC | Kriterium | Test-Referenz |
|----|-----------|---------------|
| AC-001-2-1 | `tests/README.md` beschreibt die Test-Schichten (statisch → headless → Verhalten → Hook). | informativ (Doku vorhanden) |
| AC-001-2-2 | `tests/validate.sh` läuft fehlerfrei durch (Exit-Code 0). | `bash example/tests/validate.sh` |
| AC-001-2-3 | CI prüft jede PR statisch. | `.github/workflows/validate.yml` (läuft bei jeder PR) |

---

## US-001-3 — `/greet` funktioniert (der Workflow-Trick)
> Als **Nutzer** will ich `/greet <Name>` aufrufen und eine Ein-Zeilen-Begrüßung
> bekommen, damit der Kern-Trick (Command/Skill → ein gebündelter Workflow)
> demonstriert ist.

| AC | Kriterium | Test-Referenz |
|----|-----------|---------------|
| AC-001-3-1 | `/greet <Name>` ruft den gebündelten Workflow per `scriptPath` auf. | headless `claude -p "/greet Felix"` |
| AC-001-3-2 | Der Workflow gibt strukturiert `{ who, greeting }` zurück. | `Workflow({ scriptPath: ".../greet.js", args: "Felix" })` |
| AC-001-3-3 | Die Skill `run-greet` löst denselben Workflow autonom aus, wenn die Anfrage passt. | Trigger-Prompt `claude -p "begrüße die Performance Dudes"` |
