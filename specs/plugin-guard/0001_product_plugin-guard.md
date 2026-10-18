# Product-Spec: plugin-guard — Plugins beim Start und beim Update prüfen

| | |
|---|---|
| Plugin | `plugin-guard` |
| Status | umgesetzt, Erst-Release `0.1.0` |
| Marketplace | `ai-plugins` (public) |
| Verwandt | SPEC-repo-conventions §3–§6 · `event-trace` (zeigt dieselben Events) |

## 1. Thema

Plugins führen Code auf dem Rechner aus: Shell-Hooks, MCP-Server — und seit den
Function Hooks **Hooks-Module (Mods)**, also JS/TS, das sich in die Engine selbst
einhängt: Tool-Aufrufe umschreiben, Berechtigungsentscheidungen ändern, den
System-Prompt umbauen, Umgebungsvariablen lesen und ins Netz senden. Ein Plugin, das
heute harmlos ist, kann es nach dem nächsten Update nicht mehr sein — und niemand
liest bei jedem Update den Diff.

`plugin-guard` prüft Plugins **beim Start** und **bei jedem erneuten Laden** (Update,
`/reload-plugins`, Hot-Reload) und blockiert riskante Hooks-Module, bis die Person
genau diesen Stand freigibt.

## 2. Warum (Begründung)

**Warum `plugin.register` als Gate?** Es ist der einzige Punkt, an dem ein Plugin
das Laden eines anderen Hooks-Moduls *verhindern* kann — und es feuert beim Laden
**und bei jedem Reload**. Die Engine liefert dazu `uses`: was das Modul auf `$` aufruft,
welche Events es hookt, welche Env-Variablen es liest/schreibt — exakt, weil ein
Modul diese nur literal schreiben darf. Das ist verlässlicher als jede Regex.

**Warum Hash-Pinning?** „Update" heißt: der Code ändert sich. Eine Freigabe gilt
deshalb für den SHA-256 des Codes, nicht für den Namen (Name, Version und Herkunft
sind laut Engine „its own word", also fälschbar). Neuer Code → neue Prüfung.

**Warum zusätzlich ein SessionStart-Hook?** Das Gate sieht nur, was *nach* ihm lädt,
und nur Hooks-Module. Shell-Hooks und MCP-Server kann kein Plugin blockieren. Der
Start-Audit sieht alle installierten Plugins unabhängig von der Reihenfolge und meldet
neue und geänderte.

**Warum eine Regeldatei?** Zwei Ebenen mit zwei Regelkopien würden auseinanderlaufen.
`rules/rules.json` wird von beiden gelesen; die Muster sind im gemeinsamen Teil von
JS- und Python-Regex geschrieben, ein Test kompiliert sie in beiden.

**Warum Freigaben nur per eigener Eingabe?** Sonst genügt eine Prompt-Injection, die
das Modell `/plugin-guard approve …` ausführen lässt. `command.run` trägt einen von
der Engine gestempelten `origin`; akzeptiert werden nur `composer` und `bridge`.

**Was im E2E-Lauf herauskam** (und die Regeln geprägt hat): (1) Die Reihenfolge
entscheidet — derselbe Wächter blockiert ein Plugin, das nach ihm lädt, und sieht eines
davor gar nicht. (2) Die Engine schreibt beim Laden `.claude-plugin/types/` und
`tsconfig.json` ins Plugin — ohne Ausnahme dafür ist jeder Start ein „Update". (3) Die
erste Fassung übersprang Verzeichnisse namens `types`/`.git` *überall* — ein Versteck
für importierten Schadcode. Jetzt wird nur der exakte Engine-Pfad übersprungen.

## 3. Nicht-Ziele

- Kein Beweis der Harmlosigkeit — Heuristik, die die Hürde hebt und Änderungen sichtbar macht.
- Kein Blockieren von Shell-Hooks/MCP-Servern (technisch nicht möglich), nur Melden.
- Kein Scan von Prompt-Inhalten (Skills, Agents, `*.md`) — Prompt-Injection ist ein anderes Thema.
- Keine Urteile über `builtin`- und Managed-Plugins.

## 4. Komponenten

| Komponente | Zweck |
|---|---|
| `hooks/register.ts` | Mod: `plugin.register`-Gate, Fähigkeiten-Bewertung, Hash-Pinning, `/plugin-guard` |
| `hooks/scripts/audit.sh` + `scan.py` | SessionStart-Audit aller Plugins, Änderungserkennung, CLI für CI |
| `rules/rules.json` | Quell- und Fähigkeitsregeln, eine Datei für beide Ebenen |
| `.claude-plugin/plugin.json` `userConfig.blockAt` | `high` (Default) · `critical` · `off` |

## 5. User Stories & Acceptance Criteria

### US-pg-1 — Riskante Hooks-Module laden nicht (Mod-Gate)

| AC | Soll | Test |
|----|------|------|
| AC-pg-1-1 | Jedes `user`-Hooks-Modul, das nach plugin-guard lädt, wird beim Laden **und bei jedem Reload** beurteilt; ab `blockAt` wird es mit `{ refuse }` abgelehnt, der Grund nennt Schwere, Regel und Fundstelle (`datei:zeile`). | `guard.test.ts` #1, E2E |
| AC-pg-1-2 | Saubere Module laden unverändert. | #2 |
| AC-pg-1-3 | Fähigkeiten aus `uses` zählen: geheime Env lesen + `http.fetch` = critical; `env.set` auf `PATH`/`NODE_OPTIONS`/… = critical. | #7, #8, E2E |
| AC-pg-1-4 | `builtin`/Managed-Plugins werden nicht beurteilt. | #9 |
| AC-pg-1-5 | `blockAt=off` meldet nur; `blockAt=critical` lässt `high` durch. | #10, #11 |
| AC-pg-1-6 | **Fail-closed:** scheitert die Prüfung selbst, wird blockiert. | #14 |
| AC-pg-1-7 | **Kein Versteck:** geprüft wird jede Code-Datei des Plugins (auch in Verzeichnissen namens `types/`, `.git/`, `node_modules/`); übersprungen werden nur `.claude-plugin/types/` und `tsconfig.json`/`jsconfig.json` (von der Engine geschrieben, nie ausgeführt); Symlinks werden gemeldet. | #12, `validate.sh` §4 |

### US-pg-2 — Freigabe pinnt einen Stand, ein Update braucht eine neue

| AC | Soll | Test |
|----|------|------|
| AC-pg-2-1 | `/plugin-guard approve <name>` speichert den SHA-256 des geprüften Codes; dieses Modul lädt danach. | #3, #5 |
| AC-pg-2-2 | Geänderter Code (Update) → anderer Hash → Freigabe gilt nicht, Urteil trägt `changed: true`. | #4 |
| AC-pg-2-3 | Der Hash ändert sich nicht durch Dateien, die die Engine selbst schreibt. | #13, E2E (zweiter Lauf ohne „geändert") |
| AC-pg-2-4 | `approve`/`revoke` nur bei `origin.kind` `composer` oder `bridge`. | #6 |
| AC-pg-2-5 | `/plugin-guard` zeigt alle Urteile mit Befunden; Urteile früherer Sitzungen sind markiert, der Start-Hinweis nennt nur die dieser Ladung. | #5, E2E |

### US-pg-3 — Start-Audit über alle Plugins (Hook)

| AC | Soll | Test |
|----|------|------|
| AC-pg-3-1 | Eine Regeldatei; jedes Muster kompiliert in Python **und** JavaScript. | `validate.sh` §3 |
| AC-pg-3-2 | Jede Quellregel schlägt auf ihrem Fixture an (Test schlägt fehl, wenn eine Regel ohne Fixture ist). | §4 |
| AC-pg-3-3 | Near-Misses (Download ohne Pipe, `rm -rf "$TMP"`, gepinntes `npx pkg@1.2.3`, `.example`-Dateinamen) schlagen nicht an. | §4 |
| AC-pg-3-4 | Als SessionStart-Hook: erster Lauf still; danach `systemMessage` für neue/geänderte Plugins und alles ab `high`; immer Exit 0, auch ohne python3. | §5 |
| AC-pg-3-5 | Das eigene Plugin wird übersprungen (Regeln und Tests enthalten die Muster). | §5 |
| AC-pg-3-6 | `--fail-at` setzt Exit 1 — nutzbar in CI eines Marketplace-Repos. | §5 |

## 6. Evals

Keine. Kein modellabhängiges Verhalten; Treffer/Nicht-Treffer sind deterministisch
und als Fixtures getestet. Sobald echte Fehlalarme oder Verfehlungen auftauchen,
werden sie als neue Fixture-Zeilen festgezurrt (Regel aus `CLAUDE.md`: Tasks aus
realen Failures) — die erste solche Zeile ist `.claude/settings.json.example` aus
dem `example`-Plugin.
