# 2026-10-07 — event-trace: Hooks und Mods beim Arbeiten zusehen

## Was

Neues Plugin `event-trace` (public, `0.1.0`): registriert einen klassischen
Command-Hook auf jedes Hook-Event (31) und einen Mod mit `on("*")` auf jedes
Mod-Event, und schreibt beides als JSONL nach `~/.claude/event-trace/`. Ein
Lern-/Debug-Werkzeug — es greift nicht ein.

## Was dabei herauskam

- **`on("*")` ist die einzige ehrliche Form von „alle Events".** Die Engine kennt
  ~44 Engine-Events, 33 `classic.*` und ~60 Op-Events (jeder `$`-Aufruf) — eine Liste
  wäre beim nächsten Release veraltet. Telemetrie bleibt außen vor und braucht einen
  eigenen `telemetry.*`-Hook; der Stream `anthropic` ist für Nicht-Builtins gesperrt.
- **Streaming-Events gehen auch durch `*`.** `turn.step` verlangt bei direktem Hook
  einen async Generator; der `*`-Hook bekommt per `next(e)` einfach das Endergebnis.
- **Zwei Hook-Events darf ein Logger nicht anfassen:** ein Command-Hook auf
  `WorktreeCreate`/`WorktreeRemove` *ersetzt* die Git-Logik. Bewusst ausgelassen.
- **Der Tracer sieht Secrets.** Im ersten E2E-Lauf lasen eingebaute Plugins
  `CLAUDE_CODE_SESSION_ACCESS_TOKEN` per `env.get` — ohne Redaction stünde der Wert im
  Log. Seitdem: sensible Schlüssel und `env.get`-Werte → `[redacted]`, per Test und
  per Gegenprobe gegen die echten Env-Werte belegt (0 Treffer).
- **Engine-Regel:** `$` darf nur an Top-Level-Funktionen übergeben werden — eine
  Closure `flush($)` innerhalb von `register` lädt nicht. `claude plugin validate`
  sagt das präzise.
- **Lesehilfe:** eine Zeile entsteht, wenn `next(e)` zurückkommt. Umschließende Events
  (`tool.call` um `classic.PreToolUse`/`PostToolUse`) stehen deshalb *nach* den inneren.

## Stand

`validate.sh` grün (inkl. `claude plugin validate` + 3 Mod-Tests), E2E-Lauf mit
`claude -p --plugin-dir`: 8 Hook-Events, 45 verschiedene Mod-Events (553 Zeilen).
Offen: Mod-Tests laufen in CI nicht (keine `claude`-CLI dort).
