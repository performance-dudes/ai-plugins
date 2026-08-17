# tests/terminal

**Ablage:** einteilig (SPEC-repo-conventions §5) — das Plugin ist Skill + Skript +
Template ohne Build-Subprojekt, deshalb liegt die ganze Suite code-nah beim Plugin
unter [`plugins/terminal/tests/validate.sh`](../../plugins/terminal/tests/validate.sh).
[`run.sh`](run.sh) hängt sie nur in `tests/run-all.sh` ein (Auto-Discovery über
`*/run.sh`).

**Ausführen:**

```bash
bash tests/terminal/run.sh                        # über den Aggregator
bash plugins/terminal/tests/validate.sh           # direkt, identisch
```

**Was die Suite tut:** 14 Abschnitte über die Testpyramide-Ebenen `config-valid`,
`script-run` und `skill-lint` — Manifeste, JSON-Validität, Skript-Syntax,
Badge-Escaping, beide Installer-Modi, beide Degradationspfade, Idempotenz,
Farbumrechnung und der Self-Test der Eval-Harness.

**Sandbox:** Die Suite setzt `ITERM_PROFILE_DIR` auf ein `mktemp -d` und räumt per
`trap` auf. Sie schreibt **nie** in das echte iTerm2-Profilverzeichnis — ein Testlauf
kann die Profile der ausführenden Person nicht beschädigen.

**Evals** liegen getrennt unter [`plugins/terminal/evals/`](../../plugins/terminal/evals/)
und messen Qualität (Triggering), nicht Verdrahtung. In CI läuft von dort nur der
Self-Test des Scorers — der Modell-Lauf ist manuell, weil er Tokens kostet.

Zuordnung AC ↔ Test: [`coverage.md`](coverage.md), inklusive zweier benannter Lücken.
