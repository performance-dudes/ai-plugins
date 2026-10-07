# tests/plugin-guard

**Ablage:** einteilig (SPEC-repo-conventions §5) — Hooks-Konfiguration, ein Mod-Modul,
ein Python-Skript ohne Build. Die Suite liegt code-nah unter
[`plugins/plugin-guard/tests/`](../../plugins/plugin-guard/tests/); [`run.sh`](run.sh)
hängt sie in `tests/run-all.sh` ein.

**Ausführen:**

```bash
bash tests/plugin-guard/run.sh                  # über den Aggregator
bash plugins/plugin-guard/tests/validate.sh     # direkt, identisch
claude plugin test plugins/plugin-guard         # nur die Mod-Tests (14)
```

**Was die Suite tut:**

- `config-valid` — Manifeste, `hooks.json`-Verdrahtung, `rules.json` kompiliert in
  Python **und** JavaScript, beide Ebenen lesen dieselbe Datei.
- `script-run` — jede Quellregel gegen ein **zur Laufzeit erzeugtes** Fixture (der
  Test schlägt fehl, wenn eine Regel kein Fixture hat), Near-Misses ohne Befund,
  Verstecke (`hooks/types/`, `.git/`, Symlink), der SessionStart-Audit über zwei Läufe
  (neu / geändert / still), ohne python3, `--fail-at`.
- `hook-behavior` — `tests/guard.test.ts` unter `claude plugin test`: das Gate gegen die
  echte Engine; beurteilt werden Inline-Plugins, deren `uses` die Engine selbst liest.

**Kein Angriffscode im Repo:** Fixtures entstehen in `mktemp -d` und werden per `trap`
gelöscht. Die Muster stehen nur in `rules.json` und den Tests — beides im eigenen
Plugin, das der Audit überspringt.

**Engine-Abhängigkeit:** §6 (`claude plugin validate/test`) läuft nur mit `claude`-CLI;
in CI übersprungen. Lokal vor dem PR laufen lassen.

**Evals:** keine — deterministisch (Begründung in der Spec, §6).

Zuordnung AC ↔ Test: [`coverage.md`](coverage.md).
