# Spec: Feature „Baustein-Schaukasten"

**Thema:** Von jedem Plugin-Baustein-Typ liegt **genau ein** Beispiel im Plugin —
zum Abgucken für ein eigenes Plugin.

---

## US-SHOW-1 — Jeder Baustein als kopierbare Vorlage
> Als **Plugin-Einsteiger** will ich von jedem Baustein-Typ eine Vorlage finden,
> damit ich mein eigenes Plugin daraus ableiten kann.

| AC | Kriterium | Test-Referenz |
|----|-----------|---------------|
| AC-SHOW-1-1 | Für jeden aktiven Baustein (Manifest, Workflow, Command, Skill, Subagent, Theme, Output-Style) liegt eine Beispieldatei vor. | `tests/validate.sh` Schritt 2 |
| AC-SHOW-1-2 | Alle JSON-Bausteine sind gültiges JSON. | `tests/validate.sh` Schritt 1 + 3 |
| AC-SHOW-1-3 | Das Workflow-Skript ist gültiges JavaScript. | `tests/validate.sh` Schritt 4 (`node --check`) |
| AC-SHOW-1-4 | Skill und Subagent tragen `name` + `description`. | `tests/validate.sh` Schritt 5 |
| AC-SHOW-1-5 | Auto-aktive Bausteine (Hooks, MCP, LSP, Monitore) liegen entschärft als `.example` vor. | informativ (Dateiendung `.example`) |
