# evals — workspace-context

Misst die **Qualität** des Skills, nicht seine Verdrahtung (das tut
`tests/workspace-context/validate.sh`).

## Warum keine Triggering-Suite

Der Skill setzt `disable-model-invocation: true` — er feuert **nie** von selbst,
sondern nur auf ausdrückliche Anforderung. „Triggert er richtig?" würde also ein
Config-Flag messen, und das prüft die Test-Suite bereits deterministisch.

Was tatsächlich variiert, ist das **Urteil**, das der Skill nach dem Aufruf verlangt.
Genau das misst diese Suite.

## Zwei Achsen, beide aus dem Skill selbst

**Klassifikation** — Einzelrepo oder Multi-Repo-Parent? Der Skill verlangt es
ausdrücklich: *„For a single repository, do not describe it as a sibling repository
workspace."* Ein Fehler hier erzeugt eine `AGENTS.md`, die über die Form dessen lügt,
was sie beschreibt. Die fünf Fälle enthalten die drei realen Fallen: ein **Monorepo**
(ein Repo mit internen Packages — `workspaces` im package.json ist ein
Paketmanager-Begriff, keine Sibling-Repos), ein **Meta-Repo mit eigenem `.git`** plus
gitignorierten Kindern, und ein **Worktree-Layout**, bei dem `.git` eine *Datei* ist —
wer nur nach `.git`-Verzeichnissen sucht, hält es für ein Einzelrepo.

**Zurückweisung** — erkennt der Skill eine fehlerhafte `AGENTS.md` als solche? Die
vier Fehlerfälle sind wörtlich die, die der Skill über seinen eigenen Output verbietet:
übrig gebliebener Platzhalter, kopierte Child-Build-Commands, die Überbehauptung zur
Deletion-Reconciliation, und Sibling-Formulierung für ein Einzelrepo. Dazu ein
**Clean Case**, der jedes Element des Content-Contracts erfüllt — ohne ihn bliebe
Über-Zurückweisung unbemerkt, das gegenteilige Versagen.

## Regime: deterministisch

Jede Aufgabe löst sich in **ein Label** auf (`single-repo`/`workspace` bzw.
`accept`/`reject`). Nach der Repo-Regel wird das programmatisch gematcht; ein Judge
brächte Varianz ohne zusätzliches Signal.

## Das Objekt unter Test ist die echte Skill-Datei

`--emit-prompt` liest `skills/workspace-context/SKILL.md` **zur Laufzeit**. Es gibt
keine Kopie im Harness — ändert sich der Skill, ändert sich, was gemessen wird.

## Cases sind locked

Ein Fehlschlag ist ein **Plugin-Bug**: dann wird SKILL.md geschärft, nie der Case
aufgeweicht. Jeder `note` sagt, *warum* die Erwartung so lautet.

## Ausführen

```bash
python3 evals/scripts/score_judgment.py --self-test        # ohne Modell, läuft in CI
python3 evals/scripts/score_judgment.py --emit-prompt > /tmp/p.txt
claude -p "$(cat /tmp/p.txt)" > /tmp/pred.yaml
python3 evals/scripts/score_judgment.py --predictions /tmp/pred.yaml
```

Ausgabe: Accuracy je Achse plus die konkret falschen und die fehlenden IDs. Fehlende
Vorhersagen werden als solche gemeldet, **nicht** als Fehlschlag — sonst sähe ein
abgeschnittener Lauf wie ein schlechter Skill aus.

**Ein Trial ist eine Anekdote.** Für belastbare Aussagen mehrere Trials fahren und
mean±σ berichten, für Verlässlichkeitsaussagen pass^k.
