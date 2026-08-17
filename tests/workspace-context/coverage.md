# workspace-context coverage

| Acceptance criterion | Implementation | Test |
|---|---|---|
| AC-WC-1-1 | `.claude-plugin/plugin.json`, marketplace entry | `validate.sh`, `tests/structure/check.sh` |
| AC-WC-1-2 | Public metadata and documentation | `validate.sh` hygiene scan |
| AC-WC-2-1 | `skills/workspace-context/SKILL.md` | `validate.sh` component/content checks |
| AC-WC-2-2 | Four reference templates | `validate.sh` presence, JSON parse, `bash -n` |
| AC-WC-2-3 | `reindex-workspace.sh.template` | `validate.sh` hook-contract checks |
| AC-WC-3-1 | Plugin `README.md` | Review |
| AC-WC-3-2 | Repository docs and journal | Review |

## Evals

| Achse | Suite | Regime |
|---|---|---|
| Klassifikation Einzelrepo vs. Multi-Repo-Parent | `evals/setup-judgment/cases.yaml` (5 Cases) | deterministisch |
| Erkennen einer fehlerhaften `AGENTS.md` | ebenda (4 Fehlerfälle + 1 Clean Case) | deterministisch |

**Keine Triggering-Suite, mit Begründung:** Der Skill setzt
`disable-model-invocation: true` und feuert nie von selbst. „Triggert er richtig"
würde ein Config-Flag messen, das die Test-Suite bereits deterministisch prüft. Die
Evals messen stattdessen das Urteil nach dem Aufruf — das ist die Achse, auf der ein
Modell tatsächlich variiert.

In CI läuft von den Evals nur der Self-Test des Scorers (§5): er prüft, dass die
Cases vollständig sind, dass ein Clean Case existiert (sonst bliebe Über-Zurückweisung
unbemerkt) und dass der Prompt die **echte** SKILL.md injiziert statt einer Kopie. Der
Modell-Lauf ist manuell, weil er Tokens kostet.
