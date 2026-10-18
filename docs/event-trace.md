# event-trace — wie Hooks und Mods ineinandergreifen

Erklärt die Komponenten des Plugins [`event-trace`](../plugins/event-trace/README.md)
und was man in den Logs sieht. Intent und ACs: [Spec](../specs/event-trace/0001_product_event-trace.md).

## Zwei Ebenen, ein `hooks.json`

`hooks/hooks.json` trägt beide Mechanismen nebeneinander:

```json
{
  "modules": ["./register.ts"],
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "command",
      "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/log-hook.sh\" SessionStart",
      "timeout": 5 }] }],
    "…": "ein Eintrag je Hook-Event"
  }
}
```

| | Hook (klassisch) | Mod (Function Hook) |
|---|---|---|
| Form | Shell-Kommando, ein Prozess pro Event | TS-Modul, läuft dauerhaft in eigener Umgebung |
| Input | Event-JSON auf stdin | `e` (frozen), dazu `$` (Engine) und `next` |
| Eingreifen | stdout-JSON / Exit 2 | Rückgabewert statt `next(e)`, oder `next({...e, …})` |
| Reichweite | 33 Hook-Events | jedes Engine-Event, `classic.*`, jeder `$`-Aufruf, Telemetrie |
| Ausgabe hier | `log-hook.sh` hängt an `<session>.hooks.jsonl` an | Puffer → Timer → `<session>.mods.<load>-<part>.jsonl` |

## Die Mod-Seite im Detail (`hooks/register.ts`)

- **`on("*")`** ist der Tracer. Er misst die Zeit bis `next(e)` zurückkommt, notiert
  `outcome` (`ok` / `deny` / `error`) und gibt das Ergebnis unverändert zurück. Auch
  Streaming-Events (`turn.step`, `process.spawn`) kommen hier an — der `*`-Hook bekommt
  ihr Endergebnis, z. B. bei `turn.step` Antwort, Tool-Uses, `stopReason` und Usage.
- **`next.origin`** sagt, wer das Event ausgelöst hat: `engine/core` für die Engine,
  `cc-plugin-telemetry/builtin` usw. für eingebaute Plugins. Eigene Aufrufe
  (`origin.plugin === "event-trace"`) werden übersprungen, sonst erzeugte jeder Flush
  ein neues Log-Event.
- **`on("telemetry.*", { to: "collector" })`**: `*` selektiert Telemetrie nicht. Der
  Stream `anthropic` ist den eingebauten Plugins vorbehalten — `claude plugin validate`
  lehnt ihn ab.
- **Flush:** `$.fs.write` kennt kein Append. Ein `$.clock.every(1000)` schreibt die
  laufende Teildatei neu; ab 2000 Zeilen beginnt der nächste Teil. `session.end`
  flusht zusätzlich explizit. `flush` ist eine Top-Level-Funktion, weil die Engine `$`
  nur an solche übergeben lässt.
- **Hot-Reload** startet das Modul neu: neuer `<load>`-Teil im Dateinamen, Zähler bei 0.
- **`/event-trace`** wird in `session.start` per `$.command.register` angemeldet und
  vom eigenen `command.run`-Hook beantwortet.

## Was man in einem Turn sieht (E2E-Lauf, „echo hallo")

Hook-Log, 8 Zeilen: `SessionStart → UserPromptSubmit → PreToolUse → PostToolUse →
PostToolBatch → MessageDisplay → Stop → SessionEnd`.

Mod-Log, ~550 Zeilen, 45 verschiedene Events, u. a. in dieser Reihenfolge:

```
engine.create            Plugins werden zusammengesetzt
classic.SessionStart     der klassische Hook-Pfad, als Mod-Event
session.start
prompt.section ×24       System-Prompt wird gebaut …
prompt.compose           … und zusammengesetzt
classic.UserPromptSubmit → prompt.submit → turn.start
tool.describe ×45        Tool-Beschreibungen fürs Request
turn.step  #0            Modell-Request: stopReason tool_use, Bash(echo hallo)
classic.PreToolUse → tool.check → classic.PostToolUse → tool.call
turn.step  #1            Modell-Request: "Hallo", end_turn
classic.Stop → turn.complete → classic.SessionEnd → session.end
```

Dazwischen die `$`-Aufrufe der eingebauten Plugins (`env.get`, `fs.read`,
`http.fetch`, `settings.read`) — sichtbar, weil `on("*")` auch Op-Events abdeckt.
Wichtig zum Lesen: eine Zeile wird geschrieben, wenn `next(e)` **zurückkommt** —
`seq` ist also die Abschluss-Reihenfolge. Ein Event, das andere umschließt, steht
nach ihnen: `tool.call` erscheint nach `classic.PreToolUse`, `tool.check` und
`classic.PostToolUse`, weil es sie alle umschließt — der Mod-Hook sitzt **über** dem
klassischen Hook. Ebenso kommt `prompt.submit` nach `classic.UserPromptSubmit`.

## Selbst nachvollziehen

```bash
mkdir -p /tmp/et && cd /tmp/et
echo "Run: echo hallo" | EVENT_TRACE_DIR=/tmp/et/logs \
  claude -p --plugin-dir <repo>/plugins/event-trace --allowedTools "Bash(echo:*)"
jq -r .event /tmp/et/logs/*.hooks.jsonl
jq -r .event /tmp/et/logs/*.mods.*.jsonl | grep -v '^command.describe' | uniq -c
```

## Testen

- `bash plugins/event-trace/tests/validate.sh` — statisch, Skript-Lauf, und
  (wenn `claude` installiert ist) `claude plugin validate` + `claude plugin test`.
- `claude plugin test plugins/event-trace` — die Mod-Tests (`tests/trace.test.ts`)
  gegen die echte Engine; die Test-Hooks spielen Session-Id, Dateisystem, Uhr, Env.
