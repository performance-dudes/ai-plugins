# Product-Spec: event-trace — Hooks und Mods sichtbar machen

| | |
|---|---|
| Plugin | `event-trace` |
| Status | umgesetzt, Erst-Release `0.1.0` |
| Marketplace | `ai-plugins` (public) |
| Verwandt | SPEC-repo-conventions §3–§6 · `example` (Hook-Templates) |

## 1. Thema

Claude Code kennt zwei Arten, auf das zu reagieren, was in einer Session passiert:

- **Hooks** (klassisch, Settings-/Plugin-Hooks): ein Shell-Kommando je Event-Typ
  (`PreToolUse`, `Stop`, …), das das Event als JSON auf stdin bekommt.
- **Mods** (Function-Hooks-Module): ein TypeScript-Modul, das sich mit
  `on(event, hook)` in die Engine einhängt — auf Engine-Events (`tool.call`,
  `ui.render`, `turn.step`, …), auf die klassischen Events als `classic.<Event>` und
  auf jeden Aufruf auf `$` (`fs.read`, `model.complete`, …).

Wer eines von beiden schreibt, muss zuerst wissen: **welches Event feuert wann, in
welcher Reihenfolge, mit welchem Input?** Die Doku listet Namen, aber nicht das
Zusammenspiel in einer echten Session. `event-trace` registriert sich auf **alle**
verfügbaren Hook-Events und **alle** Mod-Events und schreibt jedes Auslösen als
JSONL-Zeile in ein Logfile. Es verändert nichts — es reicht jedes Event unverändert
durch.

## 2. Warum (Begründung)

**Warum beide Ebenen in einem Plugin?** Weil der Vergleich der eigentliche
Erkenntniswert ist. Dasselbe `Stop` erscheint im Hook-Log als `Stop` und im Mod-Log
als `classic.Stop` — und drumherum sieht man im Mod-Log, was die Hooks nie sehen
(`turn.step`, `tool.check`, `prompt.compose`, die `$`-Aufrufe der eingebauten
Plugins).

**Warum `on("*")` statt einer Liste?** Die Menge der Mod-Events wächst mit jedem
Release. Eine handgepflegte Liste wäre beim nächsten Update unvollständig; der
Wildcard-Hook sieht per Definition alles, was die Engine dispatcht. Telemetrie
selektiert `*` nicht — dafür gibt es einen eigenen `telemetry.*`-Hook.

**Warum gepuffert schreiben?** `$.fs.write` schreibt eine Datei ganz; ein Append
gibt es nicht. Ein Schreibvorgang pro Event würde jedes Event (auch jedes
`ui.render`) aufs Dateisystem warten lassen. Ein Timer schreibt einmal pro Sekunde
die laufende Teildatei; ab 2000 Zeilen beginnt ein neuer Teil.

**Warum Redaction?** Der Tracer sieht alles — auch, wie eingebaute Plugins
`env.get("…_TOKEN")` lesen oder HTTP-Header schicken. Im E2E-Lauf tauchte genau das
auf. Ein Demo-Log darf keine Secrets enthalten.

## 3. Nicht-Ziele

- Kein Eingreifen: kein `deny`, kein Umschreiben, kein stdout bei Hooks.
- Keine UI (Pane/Band) — die Ausgabe ist das Logfile plus `/event-trace`.
- Kein Dauerbetrieb: das Plugin ist ein Lern-/Debug-Werkzeug. `on("*")` hängt sich in
  jedes `ui.render` — für den Alltag zu teuer.
- Keine Command-Hooks auf `WorktreeCreate`/`WorktreeRemove` (siehe AC-et-1-3).

## 4. Komponenten

| Komponente | Zweck |
|---|---|
| `hooks/hooks.json` | `hooks`: ein Command-Hook je Hook-Event · `modules`: das Mod-Modul |
| `hooks/scripts/log-hook.sh` | Command-Hook: hängt `{ts, layer:"hook", event, pid, input}` an `<session>.hooks.jsonl` |
| `hooks/register.ts` | Mod: `on("*")` + `on("telemetry.*")`, Puffer, Flush-Timer, Redaction, `/event-trace` |
| `tests/trace.test.ts` | Mod-Tests für `claude plugin test` |
| `tests/validate.sh` | Plugin-Suite (statisch + Skript-Lauf + optional `claude plugin validate/test`) |

Log-Verzeichnis: `$EVENT_TRACE_DIR`, Default `~/.claude/event-trace/`.

## 5. User Stories & Acceptance Criteria

### US-et-1 — Jeder Hook-Event wird geloggt (klassisch)

| AC | Soll | Test |
|----|------|------|
| AC-et-1-1 | `hooks.json` registriert einen Command-Hook auf **jedes** Hook-Event dieser Claude-Code-Version außer den zwei aus AC-et-1-3 (31 Events, Liste in `validate.sh`). | `validate.sh` §3 |
| AC-et-1-2 | `log-hook.sh` hängt pro Aufruf genau eine gültige JSON-Zeile mit `layer:"hook"`, Event-Name und dem kompletten stdin-Input an `<session_id>.hooks.jsonl` an. | `validate.sh` §5 |
| AC-et-1-3 | **Kein** Command-Hook auf `WorktreeCreate`/`WorktreeRemove`: dort *ersetzt* ein Command-Hook die Git-Worktree-Logik (er muss den Pfad liefern) — ein Logger würde Worktrees kaputt machen. | `validate.sh` §3 |
| AC-et-1-4 | Der Hook ist ein reiner Beobachter: **kein stdout** (bei `SessionStart`/`UserPromptSubmit` würde stdout als Kontext beim Modell landen) und **immer Exit 0**, auch bei leerem/kaputtem Input oder nicht beschreibbarem Log-Verzeichnis. | `validate.sh` §5 |

### US-et-2 — Jedes Mod-Event wird geloggt

| AC | Soll | Test |
|----|------|------|
| AC-et-2-1 | Das Mod-Modul hängt sich per `on("*")` auf alle Events und per `on("telemetry.*", {to:"collector"})` auf Telemetrie. | `validate.sh` §4, `claude plugin validate` |
| AC-et-2-2 | Jedes Event wird mit `{ts, layer:"mod", seq, event, origin, ms, outcome, input, result}` nach `<session>.mods.<load>-<part>.jsonl` geschrieben; klassische Events erscheinen als `classic.<Event>`. | `trace.test.ts` #1 |
| AC-et-2-3 | Jedes Event wird **unverändert** weitergereicht (Rückgabe = Ergebnis von `next(e)`). | `trace.test.ts` #1 |
| AC-et-2-4 | Eigene `$`-Aufrufe (Flush, Registrierung) werden nicht geloggt — kein Feedback-Loop. | `trace.test.ts` #1 |
| AC-et-2-5 | `EVENT_TRACE_DIR` überschreibt das Log-Verzeichnis. | `trace.test.ts` #2 |
| AC-et-2-6 | Werte unter sensiblen Schlüsseln (`token`, `authorization`, `api_key`, …) und `env.get`-Ergebnisse sensibler Variablen erscheinen als `[redacted]`. | `trace.test.ts` #3 |
| AC-et-2-7 | `/event-trace` zeigt die Zähler je Event und beide Log-Pfade. | `trace.test.ts` #1 |

### US-et-3 — Es funktioniert in einer echten Session

| AC | Soll | Test |
|----|------|------|
| AC-et-3-1 | Ein `claude -p --plugin-dir`-Lauf mit einem Tool-Call erzeugt beide Logs; das Mod-Log endet mit `session.end`. | manuell (E2E, Rezept in `docs/event-trace.md`) |

## 6. Evals

Keine. Das Plugin hat kein modellabhängiges Verhalten (kein Routing, kein Text, den
ein Judge bewerten müsste) — was es tut, ist deterministisch und wird vollständig
von `tests/` abgedeckt.
