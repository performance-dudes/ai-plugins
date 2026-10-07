# tests/event-trace

**Ablage:** einteilig (SPEC-repo-conventions §5) — das Plugin ist Hooks-Konfiguration,
ein Shell-Skript und ein Mod-Modul ohne Build-Subprojekt. Die Suite liegt code-nah
beim Plugin unter [`plugins/event-trace/tests/`](../../plugins/event-trace/tests/);
[`run.sh`](run.sh) hängt sie nur in `tests/run-all.sh` ein.

**Ausführen:**

```bash
bash tests/event-trace/run.sh                   # über den Aggregator
bash plugins/event-trace/tests/validate.sh      # direkt, identisch
claude plugin test plugins/event-trace          # nur die Mod-Tests
```

**Was die Suite tut:** `config-valid` (Manifest, `hooks.json`, alle 31 Hook-Events
verdrahtet, keine Worktree-Hooks, Mod-Modul eingetragen), `script-run` (`log-hook.sh`
mit gültigem, kaputtem und leerem Input, unbeschreibbares Verzeichnis — immer Exit 0,
nie stdout) und `hook-behavior` (`tests/trace.test.ts` unter `claude plugin test`:
der Mod gegen die echte Engine).

**Engine-Abhängigkeit:** `claude plugin validate`/`test` laufen nur, wenn die
`claude`-CLI installiert ist; sonst überspringt §6 sie mit Hinweis (CI hat sie
nicht). Lokal vor dem PR laufen lassen.

**Sandbox:** `EVENT_TRACE_DIR` zeigt auf ein `mktemp -d`; nichts landet in
`~/.claude/event-trace/`.

**Evals:** keine — kein modellabhängiges Verhalten (Begründung in der Spec, §6).

Zuordnung AC ↔ Test: [`coverage.md`](coverage.md).
