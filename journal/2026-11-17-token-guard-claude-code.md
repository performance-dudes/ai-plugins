# 2026-11-17 — token-guard für Claude Code

## Anlass

Das opencode-Plugin `opencode-token-guard` bremst Token-Burn (Bash-Serien,
Verify-Churn, Step- und Kontext-Budget, Projekt-Ausbruch, Offload-Asks). Das Team
arbeitet aber überwiegend in Claude Code. Ziel: dieselben Wächter als
Claude-Code-Plugin `token-guard`, ohne das opencode-Plugin anzufassen.

## Ergebnis

- Plugin `plugins/token-guard` 0.1.0: ein Hook-Einstieg für `PreToolUse`,
  `PostToolUse`, `Stop`, `UserPromptSubmit` und `SessionEnd`, Regeln von Hand aus
  `guard.ts` nach `hooks/lib/guard.mjs` übertragen, Zustand pro Session in einer
  Datei, Command `/token-guard:token-guard`.
- Spec `SPEC-token-guard` mit 8 User Stories, Tests unter `tests/token-guard/`
  (23 Tests, grün), Eval-Suite `plugins/token-guard/evals/offload/` (24/24, pass^3).
- E2E (AC-tg-8-1), manuell: headless `claude -p --plugin-dir …` mit
  `TOKEN_GUARD_MAX_CONSECUTIVE_BASH=2`. Der dritte Einzweck-Bash-Call wurde abgelehnt,
  das Modell hat die Begründung wörtlich gesehen, der vierte lief wieder durch,
  `blockedBashStreaks = 1`, die Session-Datei war nach Sessionende gelöscht.
  `/token-guard:token-guard` gab die Statistik in einer echten Session korrekt aus.

## Entscheidungen

- **Kopie statt gemeinsamer Bibliothek.** Das opencode-Plugin bleibt unberührt, und
  ein Claude-Code-Plugin muss ohne Build aus dem Marketplace laufen. Gegen Drift
  läuft `parity.test.mjs`: Kopie und gebautes Original auf denselben Fixtures; jede
  bewusste Abweichung ist als solche markiert und wird darauf geprüft, dass sie sich
  noch unterscheidet.
- **Node als Laufzeit**, ohne Abhängigkeiten. Fehlt Node, endet der Hook über
  `command -v node` mit Exit 0 (Fail-open).
- **Zustand in Dateien mit Lock.** Claude Code startet pro Hook-Event einen neuen
  Prozess, parallele Tool-Calls laufen gleichzeitig. Ohne Lock gingen Zählungen
  verloren (Test mit 8 parallelen Schreibern).
- **Hinweise aus `Stop`** gehen sofort als `systemMessage` an den User und mit dem
  nächsten Prompt als `additionalContext` ans Modell. `Stop` blockt nie.

## Learnings

- **Das Vorbild hatte drei stille Fehler**, die erst der Readiness-Check
  (`/spec:spec-confidence`) und die Eval sichtbar machten: Die Verify-Drossel konnte
  nie feuern (`onBashBefore` setzt den Edit-Zähler vor dem Lauf auf 0), `cd /tmp`
  galt als Ausbruch (Allowlist verlangt Schrägstrich), und der Offload-Detektor
  verfehlte *create/do/edit*, *Erstelle*, *von Hand* und meldete Ich-Sätze (18/24
  im ersten Lauf). Alle drei sind im neuen Plugin behoben und in Spec §6a als
  Abweichung geführt.
- **Erster Readiness-Check nicht grün** (Baubarkeit 98 %, Abnahmeschärfe 91 %, eine
  bestätigte Blockade an der Allowlist, zwei Abweichungen bei `0`/Fehlwerten). Die
  Spec wurde geschärft; ein zweiter Messpunkt steht aus.
- **Plugin-Commands sind immer namespaced** (`/<plugin>:<command>`); ein
  `/token-guard` gibt es nicht.
- **Tests unter macOS:** `tmpdir()` liegt unter `/var/folders` und damit in der
  Allowlist. „Außerhalb"-Pfade in Tests müssen woanders liegen (`/srv/…`).
- **`claude -p`:** `--allowedTools` ist variadisch und schluckt einen danach
  stehenden Prompt. Den Prompt vor die Flags stellen.

## Abweichungen vom Prozess

Der Spec-PR wurde nicht als erster Schritt geöffnet. Auf Wunsch wurde erst gebaut
und lokal erprobt; Spec, Tests, Evals, Code und Docs kommen in einem PR.

## Follow-ups

- Issue: die drei Fehler im opencode-Plugin (Verify-Drossel, `/tmp`-Allowlist,
  Offload-Lücken) dort beheben.
- Zweiter Readiness-Messpunkt auf der geschärften Spec.
- Eval-Cases aus echten Sessions nachziehen, sobald Fehlschläge auftreten.
