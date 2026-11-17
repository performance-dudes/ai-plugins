# Product-Spec: `token-guard` — Token-Burn-Leitplanke für Claude Code

Spec-ID: `SPEC-token-guard` · Status: Entwurf · Datum: 2026-11-17 · Autor: Yannik (mit Claude)

Gilt für das Plugin `plugins/token-guard` im öffentlichen Marketplace `ai-plugins`.
Methodik: `SPEC-repo-conventions` (Spec-Driven TDD, Struktur, Tests).
Vorbild: das opencode-Plugin `plugins/opencode/opencode-token-guard` (gleiche Regeln,
anderer Host).

---

## 1. Thema

Ein Claude-Code-Plugin, das lange Agent-Sessions gegen **Token-Burn** absichert:

> Kosten ≈ Provider-Steps × Kontextgröße

Jeder Step liest die komplette Konversation erneut (größtenteils aus dem Cache, aber
auch Cache-Reads zählen gegen Kosten und Kontingent). Das Plugin greift die
Verhaltensmuster an, die dieses Produkt explodieren lassen, und setzt weiche Budgets
auf Session-Länge und Kontextgröße. Es ist ein **Stolperdraht, kein Autopilot**: es
blockt einzelne Tool-Calls mit Begründung und gibt Hinweise, es schreibt nie eine
Session um.

Die sechs Wächter des opencode-Plugins werden übernommen; bewusste Abweichungen vom Vorbild stehen in §5 (markiert mit **Abweichung**) und gesammelt in §6a:

| Wächter | Verhalten | Default |
|---|---|---|
| Bash-Rationierung | blockt eine Serie aufeinanderfolgender *Einzweck*-Bash-Calls; verkettete (`&&`, `\|\|`, `;`, Schleifen) und Verifikations-Befehle zählen nie | Block nach **8** |
| Verify-Drossel | Hinweis, wenn Test/Lint/Typecheck nach weniger als N Edits seit dem letzten Lauf läuft | N = **3** |
| Step-Budget | einmaliger Hinweis, wenn die Session N Assistant-Steps überschreitet | N = **200** |
| Kontext-Budget | einmaliger Hinweis, wenn der Kontext N Input-Tokens (inkl. Cache) überschreitet | N = **150 000** |
| Projekt-Ausbruch | blockt Bash-Befehle, die Dateisystem-Zustand **außerhalb** des Projekt-Roots verändern | immer an |
| Offload-Ask | Hinweis, wenn der Assistant den User bittet, Projektarbeit selbst bzw. außerhalb des Projekts zu erledigen | immer an |

Dazu ein Command `/token-guard`, der die gesammelten Auslöse-Statistiken berichtet.

## 2. Warum (Begründung)

- **Das Kostenproblem ist host-unabhängig.** Claude Code hat dieselbe Kostenformel wie
  opencode. Die Regeln des opencode-Plugins sind in Produktion erprobt (Metrik-Datei
  mit Auslösungen seit 2026-08); sie gehören auch in den Host, den das Team
  hauptsächlich nutzt.
- **In Claude Code sieht das Modell die Hinweise.** Im opencode-Plugin landen
  Verify-, Step- und Kontext-Hinweise nur als WARN-Zeile im Log — das Modell sieht sie
  nie, wirksam sind dort nur die Blocks. Claude-Code-Hooks können Hinweise per
  `additionalContext` direkt in den Modell-Kontext legen. Die Portierung ist damit
  nicht nur gleichwertig, sondern wirksamer. Einschränkung: Hinweise, die erst am
  Turn-Ende (`Stop`-Hook) entstehen, erreichen das Modell verzögert, beim nächsten
  User-Prompt (AC-tg-3-4); der User sieht sie sofort.
- **Pure Logik ist portabel.** Die Entscheidungslogik (`guard.ts`) hat keine
  opencode-Abhängigkeit. Nur die Verdrahtung an den Host ändert sich.
- **Kopie statt geteilter Bibliothek (bewusst).** Die Logik wird ins neue Plugin
  kopiert, nicht in ein gemeinsames Paket ausgelagert: das opencode-Plugin bleibt
  unberührt, und ein Claude-Code-Plugin muss ohne Build-Schritt aus dem Marketplace
  laufen. Drift-Risiko wird über gemeinsame Test-Fixtures adressiert (US-tg-7).

## 3. Nicht-Ziele

- Kein Sandbox-Ersatz: Projekt-Ausbruch ist eine Heuristik auf dem Befehlstext, keine
  Sicherheitsgrenze. Bewusst konservativ in beide Richtungen.
- Kein Umschreiben von Tool-Calls, kein automatisches `/compact`, kein Abbruch einer
  Session. Blocks betreffen immer genau einen Tool-Call.
- Keine Änderung am opencode-Plugin.
- Keine Skills, Agents oder MCP-Server — nur Hooks plus ein Command.
- Kein Build-Schritt: das Plugin läuft direkt aus dem Marketplace-Checkout.

## 4. Host-Abbildung (opencode → Claude Code)

| opencode | Claude Code |
|---|---|
| ein langlebiger Plugin-Prozess pro Session, Zustand im Speicher | ein neuer Prozess pro Hook-Event; Zustand in einer Datei pro `session_id` |
| `tool.execute.before` + `throw` | `PreToolUse`-Hook, Entscheidung `deny` mit Begründung (für das Modell sichtbar) |
| `tool.execute.after` | `PostToolUse`-Hook, Hinweis per `additionalContext` |
| `edit` / `write` | `Edit`, `Write`, `NotebookEdit` |
| `message.updated` mit Token-Zählern | Auswertung des Session-Transcripts (`transcript_path`): Assistant-Steps zählen, Usage der letzten Antwort lesen |
| gestreamte Text-Parts | `Stop`-Hook liest die letzte Assistant-Antwort aus dem Transcript |
| `client.app.log` (WARN) | Hinweis an das Modell (`additionalContext`) und an den User (`systemMessage`) |
| `directory` | `CLAUDE_PROJECT_DIR`, Fallback `cwd` aus dem Hook-Input |
| `~/.local/share/opencode/token-guard-metrics.json` | `~/.claude/token-guard-metrics.json` |

## 5. User Stories & Acceptance Criteria

Test-Typen nach `SPEC-repo-conventions` §6 (`config-valid`, `script-run`,
`hook-behavior`, `e2e`); `script-run` umfasst hier die Unit-Tests der puren Logik
(Pyramiden-Stufe 2, §5). Die Eval-Suite folgt `ai-plugins/CLAUDE.md` (Abschnitt
Eval-Logik) und liegt wie bei `mechanic` im Plugin unter `evals/`. Testpfade ohne
Präfix sind relativ zu `tests/token-guard/`.

### US-tg-1 — Bash-Serien werden gestoppt

Als Nutzer will ich, dass eine Serie einzelner Bash-Calls geblockt wird, damit der
Agent verkettet oder parallelisiert statt pro Befehl einen Step zu bezahlen.

| AC | Soll | Test |
|----|------|------|
| AC-tg-1-1 | Ein Bash-Befehl wird als `verify`, `chained` oder `single` klassifiziert, mit denselben Regeln wie das opencode-Plugin. | script-run `guard.test` |
| AC-tg-1-2 | Der (N+1)-te aufeinanderfolgende `single`-Bash-Call einer Session wird per `PreToolUse` mit Entscheidung `deny` abgelehnt; die Begründung nennt die Seriengröße und fordert Verketten oder Parallelisieren. | hook-behavior `hooks.test` |
| AC-tg-1-3 | Ein `chained`- oder `verify`-Call setzt den Serienzähler zurück; nach einem Block beginnt die Zählung neu. | script-run + hook-behavior |
| AC-tg-1-4 | Nicht-Bash-Tools verändern den Serienzähler nicht. | hook-behavior |
| AC-tg-1-5 | Der Zähler überlebt zwischen Hook-Prozessen derselben Session und ist zwischen Sessions getrennt. | hook-behavior `hooks.test` |

### US-tg-2 — Verify-Churn wird dem Modell gemeldet

Als Nutzer will ich, dass der Agent erfährt, wenn er nach zu wenigen Änderungen
testet, damit er Änderungen bündelt.

| AC | Soll | Test |
|----|------|------|
| AC-tg-2-1 | `Edit`, `Write` und `NotebookEdit` erhöhen den Edit-Zähler der Session. | hook-behavior |
| AC-tg-2-2 | Läuft ein `verify`-Befehl nach 1 bis N−1 Edits, liefert `PostToolUse` einen Hinweis als `additionalContext`; bei 0 oder ≥ N Edits keinen. | hook-behavior `hooks.test` |
| AC-tg-2-3 | Nur der `verify`-Lauf in `PostToolUse` setzt den Edit-Zähler auf 0; `PreToolUse` setzt bei `verify` nur den Bash-Serienzähler zurück. **Abweichung:** im Vorbild setzt schon `onBashBefore` den Edit-Zähler zurück (`guard.ts:61`), sodass `onVerifyAfter` immer 0 liest und der Hinweis nie feuert. | script-run |

### US-tg-3 — Weiche Budgets für Session-Länge und Kontext

Als Nutzer will ich einen einmaligen Hinweis, wenn eine Session zu lang oder der
Kontext zu groß wird, damit ich rechtzeitig kompaktiere oder neu starte.

| AC | Soll | Test |
|----|------|------|
| AC-tg-3-1 | Assistant-Steps werden aus dem Transcript gezählt; mehrere Transcript-Zeilen derselben API-Antwort (gleiche Message-ID) zählen als ein Step. | script-run `metrics.test` |
| AC-tg-3-2 | Die Kontextgröße ist `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` der letzten Assistant-Antwort. | script-run `metrics.test` |
| AC-tg-3-3 | Die Budgets werden in `PostToolUse` **und** im `Stop`-Hook ausgewertet (ein Turn ohne Tool-Call hat nur `Stop`). Beim ersten Überschreiten des Step- bzw. Kontext-Budgets entsteht genau ein Hinweis pro Budget und Session — in dem Hook, der das Überschreiten zuerst sieht; ein Flag im Session-Zustand verhindert einen zweiten. | hook-behavior |
| AC-tg-3-4 | Ein in `PostToolUse` entstandener Hinweis geht als `additionalContext` an das Modell. Ein im `Stop`-Hook entstandener Hinweis geht sofort als `systemMessage` an den User und wird beim nächsten `UserPromptSubmit` als `additionalContext` nachgereicht. | hook-behavior |
| AC-tg-3-5 | Das Transcript wird inkrementell gelesen (Byte-Offset im Session-Zustand), nicht bei jedem Event komplett. | script-run `metrics.test` |

### US-tg-4 — Kein Ausbruch aus dem Projekt

Als Nutzer will ich, dass Bash-Befehle, die außerhalb des Projekts schreiben, geblockt
werden, damit der Agent bei Reibung nicht in fremde Verzeichnisse ausweicht.

| AC | Soll | Test |
|----|------|------|
| AC-tg-4-1 | Erkennung wie `mutatesOutsideProject` im Vorbild (`guard.ts:164-190`): Redirect-Ziel außerhalb; Pfad-Operand außerhalb bei `mkdir`, `touch`, `rm`, `tee`, `ln`, `truncate` und `sed -i`; `cd` nach außerhalb plus Schreibhinweis (`mv`, `cp`, `rsync`, `install` u. a. zählen nur in dieser Kombination). Lesen von außerhalb wird nicht geblockt. Allowlist: `/tmp`, `/private/tmp`, `/dev`, `/var/folders` **jeweils inklusive des Verzeichnisses selbst** (`cd /tmp && touch x` ist erlaubt). **Abweichung:** im Vorbild verlangt die Allowlist einen Schrägstrich nach dem Namen (`guard.ts:132`), dort gilt `cd /tmp` als außerhalb. | script-run `guard.test` |
| AC-tg-4-2 | Projekt-Root ist `CLAUDE_PROJECT_DIR`, sonst `cwd` aus dem Hook-Input. | hook-behavior |
| AC-tg-4-3 | Ein erkannter Befehl wird per `PreToolUse` mit `deny` und der Begründung des opencode-Plugins (angepasst auf Claude-Code-Toolnamen) abgelehnt. Die Prüfung läuft vor der Bash-Rationierung. | hook-behavior `hooks.test` |

### US-tg-5 — Offload-Asks werden erkannt

Als Nutzer will ich, dass der Agent korrigiert wird, wenn er mich bittet, Projektarbeit
selbst bzw. außerhalb des Projekts zu erledigen.

| AC | Soll | Test |
|----|------|------|
| AC-tg-5-1 | Der `Stop`-Hook prüft den Text der letzten Assistant-Antwort (`last_assistant_message` aus dem Hook-Input, sonst aus dem Transcript) satzweise mit den Offload-Mustern des opencode-Plugins (de + en). **Abweichung (eval-getrieben):** zusätzliche Verben (*create, do, edit, …*; *erstelle, leg, mach, …*), *von Hand*/*händisch*, der `erstell\b`-Fehler auf „Erstelle" behoben, und ein Satz in der ersten Person, der den User nicht anspricht, gilt nicht als Offload. | script-run `guard.test` + `parity.test` + hook-behavior `hooks.test` |
| AC-tg-5-2 | Bei Treffer gilt dieselbe Zustellung wie AC-tg-3-4 (User sofort, Modell beim nächsten Prompt). Der `Stop`-Hook blockt das Turn-Ende nie. | hook-behavior |
| AC-tg-5-3 | Die Erkennung erreicht auf der festgezurrten Eval-Suite `plugins/token-guard/evals/offload/` pass^3 = 100 % auf allen Positiv- und Near-Miss-Cases. | Eval-Suite `plugins/token-guard/evals/offload/` |

### US-tg-6 — Metriken und `/token-guard`

Als Nutzer will ich sehen, wie oft das Plugin ausgelöst hat und was es grob gespart
hat.

| AC | Soll | Test |
|----|------|------|
| AC-tg-6-1 | Jede Auslösung erhöht in `~/.claude/token-guard-metrics.json` (überschreibbar per `TOKEN_GUARD_METRICS_PATH`) den Zähler ihrer Art, `total`, `firstFiring`/`lastFiring` und bei der ersten Auslösung einer Session `sessions`. Schema-Felder wie im opencode-Plugin. | script-run `metrics.test` |
| AC-tg-6-2 | Parallele Hook-Prozesse verlieren keine Zählung (atomares Schreiben). | script-run `metrics.test` |
| AC-tg-6-3 | Ein mitgeliefertes Skript gibt die Statistik deterministisch aus (Zähler je Art, Sessions, Zeitraum, beschriftete Schätzung gesparter Steps). `/token-guard` ruft nur dieses Skript und gibt seine Ausgabe wieder. | script-run `metrics.test` |

### US-tg-7 — Konfiguration, Robustheit, Parität

| AC | Soll | Test |
|----|------|------|
| AC-tg-7-1 | Schwellwerte über dieselben Variablennamen wie im opencode-Plugin: `TOKEN_GUARD_MAX_CONSECUTIVE_BASH`, `TOKEN_GUARD_MIN_EDITS_PER_VERIFY`, `TOKEN_GUARD_STEP_BUDGET`, `TOKEN_GUARD_CONTEXT_BUDGET`. Gesetzt ist ein Wert nur als ganze Zahl `^[0-9]+$`; alles andere (leer, `abc`, `8abc`, `2.5`, negativ) gilt als nicht gesetzt (Default). Wert `0` schaltet den jeweiligen Wächter ab. Projekt-Ausbruch und Offload-Ask haben keinen Schwellwert und sind immer an. **Abweichung:** im Vorbild wird jeder Wert per `parseInt` übernommen (`NaN` schaltet die Bash-Rationierung still ab, `0` blockt jeden Einzel-Call bzw. feuert die Budgets sofort). | script-run |
| AC-tg-7-2 | **Fail-open:** jeder interne Fehler (Zustand unlesbar oder korrupt, Transcript fehlt, ungültiger Hook-Input, `session_id` nicht `[A-Za-z0-9_-]+`) endet mit Exit 0 ohne Entscheidung. Fehlt Node, beendet der Shell-Aufruf in `hooks.json` den Hook vor dem Start mit Exit 0. Ein korrupter Zustand wird beim nächsten Schreiben durch einen frischen ersetzt. Das Plugin blockt nie wegen eines eigenen Fehlers. | hook-behavior `hooks.test` |
| AC-tg-7-3 | Session-Zustand liegt unter `~/.claude/token-guard/sessions/<session_id>.json` und wird beim `SessionEnd`-Hook gelöscht. | hook-behavior |
| AC-tg-7-4 | Jeder Hook antwortet in unter 200 ms (Median über 20 Läufe auf einem Fixture-Transcript mit 2 000 Zeilen). | script-run `metrics.test` |
| AC-tg-7-5 | Parität: eine Fixture-Liste `tests/token-guard/fixtures/parity.json` (Bash-Befehle, Befehl+Root-Paare, Assistant-Texte) wird gegen die Kopie **und** gegen das gebaute Vorbild `plugins/opencode/opencode-token-guard/dist/guard.js` ausgeführt; `classifyBash`, `mutatesOutsideProject` und `isOffloadAsk` liefern dasselbe, außer bei Fällen, die als bewusste Abweichung (AC-tg-4-1) markiert sind. | script-run `parity.test` |
| AC-tg-7-6 | Manifest valide, im Marketplace registriert, Version synchron (`SPEC-repo-conventions` US-conv-4/5). | config-valid `tests/structure/check.sh` |

### US-tg-8 — Echte Session (E2E)

| AC | Soll | Test |
|----|------|------|
| AC-tg-8-1 | In einer headless Session (`claude -p`) mit aktiviertem Plugin und `TOKEN_GUARD_MAX_CONSECUTIVE_BASH=2` wird der dritte Einzweck-Bash-Call geblockt, und die Metrik-Datei zeigt `blockedBashStreaks ≥ 1`. Läuft nicht in CI (braucht Login), sondern manuell vor dem Merge; Ergebnis im Journal. | e2e `e2e.sh` |

## 6. Bekannte Reibung

Der Workspace-`CLAUDE.md` von Performance Dudes verlangt „ein Befehl nach dem anderen"
— genau das Muster, das die Bash-Rationierung nach 8 Calls blockt. Wer das Plugin dort
nutzt, setzt `TOKEN_GUARD_MAX_CONSECUTIVE_BASH` höher oder auf `0`. Die Plugin-Doku
nennt das ausdrücklich.

## 6a. Bewusste Abweichungen vom Vorbild

| Thema | Vorbild (opencode) | token-guard (Claude Code) | AC |
|---|---|---|---|
| Verify-Drossel | feuert nie (Edit-Zähler wird vor dem Lauf genullt) | feuert wie beschrieben | AC-tg-2-3 |
| Allowlist | `/tmp` selbst gilt als außerhalb | `/tmp` selbst ist erlaubt | AC-tg-4-1 |
| Wert `0` / Fehlwerte | `parseInt` ungeprüft | `0` = aus, Fehlwert = Default | AC-tg-7-1 |
| Offload-Erkennung | 18/24 auf `evals/offload/` (verfehlt *create/do/edit*, *Erstelle*, *von Hand*; meldet Ich-Sätze) | 24/24 | AC-tg-5-1, AC-tg-5-3 |
| Hinweise | nur im Log | im Modell-Kontext | AC-tg-2-2, AC-tg-3-4 |

Die ersten beiden und die Offload-Lücken sind Fehler im Vorbild; sie dort zu beheben ist nicht Teil dieser
Spec (Nicht-Ziel „Keine Änderung am opencode-Plugin"), wird aber als Issue nachgezogen.

## 7. Offen

- (entschieden 2026-11-17) Laufzeit: Node ≥ 18 (ESM, ohne Abhängigkeiten), die Logik
  von Hand aus `guard.ts`/`metrics.ts` nach `.mjs` übertragen. Ohne Node greift
  Fail-open (AC-tg-7-2): wirkungslos, aber harmlos.
- (entschieden 2026-11-17) Name: `token-guard` (Plugin-ID `token-guard@ai-plugins`).
- Parallele Hook-Prozesse derselben Session: der Session-Zustand wird unter einer
  Lock-Datei gelesen und geschrieben (kurzes Warten, danach Fail-open). Parallele
  Einzweck-Bash-Calls in einem Tool-Block zählen wie im Vorbild einzeln zur Serie.
