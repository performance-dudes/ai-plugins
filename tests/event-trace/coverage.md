# Coverage — event-trace

Traceability nach SPEC-repo-conventions §6. Spec:
[`specs/event-trace/0001_product_event-trace.md`](../../specs/event-trace/0001_product_event-trace.md).
Suite: [`plugins/event-trace/tests/validate.sh`](../../plugins/event-trace/tests/validate.sh)
(§n) und [`trace.test.ts`](../../plugins/event-trace/tests/trace.test.ts) (#n).

## spec : code

| AC | umsetzende Komponente |
|---|---|
| AC-et-1-1 alle Hook-Events | `hooks/hooks.json` (`hooks`) |
| AC-et-1-2 eine JSONL-Zeile je Aufruf | `hooks/scripts/log-hook.sh` |
| AC-et-1-3 keine Worktree-Hooks | `hooks/hooks.json` (bewusst ausgelassen) |
| AC-et-1-4 still, Exit 0 | `log-hook.sh` (kein stdout, `exit 0` auf jedem Pfad) |
| AC-et-2-1 `on("*")` + Telemetrie | `hooks/register.ts`, `hooks/hooks.json` (`modules`) |
| AC-et-2-2 Log-Format/Datei | `register.ts` → `record`, `flush`, `fileOf` |
| AC-et-2-3 unverändert durchreichen | `register.ts` (`return result` aus `next(e)`) |
| AC-et-2-4 keine Eigen-Events | `register.ts` (`next.origin.plugin === 'event-trace'`) |
| AC-et-2-5 `EVENT_TRACE_DIR` | `register.ts` (`session.start`), `log-hook.sh` |
| AC-et-2-6 Redaction | `register.ts` → `redact`, `isSecretRead` |
| AC-et-2-7 `/event-trace` | `register.ts` (`command.register` + `command.run`) |
| AC-et-3-1 echte Session | Plugin als Ganzes |

## spec : test

| AC | Test | Typ |
|---|---|---|
| AC-et-1-1 | §3 Event-Menge == erwartete 31, je ein `log-hook.sh <Event>` | config-valid |
| AC-et-1-2 | §5 genau eine gültige Zeile, `layer`/`event`/`input`; Append | script-run |
| AC-et-1-3 | §3 kein `WorktreeCreate`/`WorktreeRemove` | config-valid |
| AC-et-1-4 | §5 kein stdout, Exit 0 bei gültigem, kaputtem Input und unbeschreibbarem Dir | script-run |
| AC-et-2-1 | §4 `modules`, `on('*'`, `telemetry.*` · §6 `claude plugin validate` | config-valid |
| AC-et-2-2 | #1 Dateiname, `layer:"mod"`, `classic.Stop` im Log | hook-behavior |
| AC-et-2-3 | #1 `classic.Stop` liefert `{}` unverändert, alle `outcome:"ok"` | hook-behavior |
| AC-et-2-4 | #1 kein `fs.write`/`session.id` im Log | hook-behavior |
| AC-et-2-5 | #2 Pfad unter `/var/trace` | hook-behavior |
| AC-et-2-6 | #3 `[redacted]`, kein `sk-geheim` | hook-behavior |
| AC-et-2-7 | #1 Zusammenfassung nennt Event und Hook-Log | hook-behavior |
| AC-et-3-1 | manuell, Rezept in `docs/event-trace.md` | e2e |

## code : tests

| Komponente | config-valid | script-run | hook-behavior | e2e |
|---|---|---|---|---|
| `hooks/hooks.json` | §2, §3, §4 | — | — | manuell |
| `hooks/scripts/log-hook.sh` | §2 (`bash -n`) | §5 | — | manuell |
| `hooks/register.ts` | §4, §6 validate | — | #1–#3 | manuell |

## Lücken

- **`env.get`-Redaction** (zweiter Teil von AC-et-2-6) ist nur im E2E-Lauf belegt: die
  Test-Engine hat kein `env`-Nomen, über das ein fremder Aufrufer `env.get` auslösen
  könnte. Der Schlüssel-Pfad (`redact`) ist automatisch getestet.
- **E2E** (AC-et-3-1) läuft manuell — braucht Login und kostet Tokens.
- **§6 in CI**: ohne `claude`-CLI übersprungen; die Mod-Tests laufen also nur lokal.
