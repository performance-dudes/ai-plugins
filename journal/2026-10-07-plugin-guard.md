# 2026-10-07 — plugin-guard: ein Gate vor jedem Hooks-Modul

## Was

Neues Plugin `plugin-guard` (public, `0.1.0`). Ein Mod auf `plugin.register` beurteilt
jedes Hooks-Modul beim Laden und bei jedem Reload/Update — Quelltext gegen
`rules/rules.json`, Fähigkeiten aus `e.uses`, SHA-256-Pin — und lehnt ab `high` ab, bis
die Person genau diesen Stand freigibt. Ein SessionStart-Hook auditiert zusätzlich alle
installierten Plugins (inkl. Shell-Hooks/MCP) und meldet neue und geänderte.

## Was dabei herauskam

- **`plugin.register` ist der Hebel.** Es feuert beim Laden *und* beim Reload, kann
  `{ refuse }` antworten, und die Engine liefert `uses` exakt — weil ein Modul `$`, `on`
  und `$.env` nur literal schreiben darf. Fähigkeiten schlagen Regex.
- **Reihenfolge entscheidet.** E2E: Wächter vor dem Plugin → blockiert; danach →
  „judged by core alone: admitted". Volle Abdeckung nur als Managed-Plugin (`prepend`).
- **Abgelehnt heißt: geladen, dann ausgefaltet.** `register()` des abgelehnten Moduls
  läuft (Sandbox, `$` leer); beitreten tut nichts. Ehrlich so dokumentiert.
- **Die Engine schreibt ins Plugin** (`.claude-plugin/types/`, `tsconfig.json`) —
  ohne Ausnahme wäre jeder Start ein Update. Die erste Ausnahme war zu breit
  (Verzeichnisname `types`/`.git` überall) und damit ein **Versteck** für importierten
  Schadcode; jetzt nur der exakte Pfad. Regressionstest in beiden Ebenen.
- **Urteile im `$.store` überleben Sitzungen** — der erste Start-Toast meldete ein
  Plugin als blockiert, das gar nicht geladen war. Jetzt nur Urteile dieser Ladung.
- **Fehlalarme aus dem eigenen Repo** wurden Near-Miss-Fixtures:
  `.claude/settings.json.example` (Settings-Regel jetzt nur bei Schreibzugriff),
  `os.environ.get("…_API_KEY")` in API-Clients (Quellregel `medium`; im Gate zählt die
  Fähigkeit, mit Netz `critical`).
- **Freigaben nur per eigener Eingabe** (`origin.kind` `composer`/`bridge`), sonst
  genügt eine Prompt-Injection.

## Stand

`validate.sh` grün (13 Regeln mit Fixtures, Near-Misses, Verstecke, Audit über zwei
Läufe, `claude plugin validate`, 14 Mod-Tests). E2E mit `claude -p --plugin-dir`:
`evil-helper` blockiert (critical: Token + Netz), `event-trace` zugelassen (medium: `*`),
zweiter Lauf ohne „geändert". Repo-Scan der eigenen 11 Plugins: höchster Befund medium.
Offen: Mod-Tests in CI (keine `claude`-CLI), Managed-Rollout-Anleitung.
