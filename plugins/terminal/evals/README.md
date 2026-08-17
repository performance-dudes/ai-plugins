# evals — terminal

Misst die **Qualität** des Plugins, nicht seine Verdrahtung (das tut
`tests/validate.sh`). Konkret die Kern-Promise des Skills: **feuert er bei den
richtigen Anfragen — und schweigt bei den benachbarten?**

## Regime: deterministisch

Der Output je Task ist STRUCTURED — genau ein Label (`fires` / `no`). Nach der
Repo-Regel wird das **programmatisch gematcht**, nicht von einem Judge bewertet: ein
Judge brächte hier nur Varianz und Kosten, ohne etwas zu messen, das ein exakter
Vergleich nicht sieht.

## Das Objekt unter Test ist die echte Skill-Datei

`score_triggering.py --emit-prompt` liest
`skills/iterm-dynamic-profile/SKILL.md` **zur Laufzeit** und legt sie in den Prompt.
Es gibt keine Kopie im Harness. Ändert sich der Skill, ändert sich automatisch, was
gemessen wird — eine gepflegte dritte Kopie wäre per Definition kein Test des
Plugins. `tests/validate.sh` §14 prüft genau das nach.

## Cases sind locked

`triggering/cases.yaml` ist eingefroren. **Ein Fehlschlag ist ein Plugin-Bug** — dann
wird die `description` des Skills geschärft, nie der Case aufgeweicht. Jeder `note`
ist der Kalibrier-Anker: er sagt, *warum* die Erwartung so lautet, damit zwei Leute
zum selben Pass/Fail-Urteil kämen.

16 Tasks: **10 positive**, **5 Near-Miss** und **1 Clean Case**. Die sechs negativen
tragen die Precision — ein Skill, der auf alles Terminal-Förmige anspringt, ist
wertlos. Die Near-Misses sind bewusst nah: Statuszeile, zsh-Prompt, Ghostty,
Editor-Theme, tmux. Sprache und Formulierung variieren (de/en, explizit/implizit,
Slash-Command), damit Intent-Verständnis gemessen wird und nicht ein Prompt-Template.

## Ausführen

```bash
python3 evals/scripts/score_triggering.py --self-test          # ohne Modell, läuft in CI
python3 evals/scripts/score_triggering.py --emit-prompt > /tmp/p.txt
claude -p "$(cat /tmp/p.txt)" > /tmp/pred.yaml                 # ein trial
python3 evals/scripts/score_triggering.py --predictions /tmp/pred.yaml
```

Ausgabe: Confusion-Matrix plus Precision, Recall, F1, Specificity. Fehlende
Vorhersagen werden als solche gemeldet und **nicht** als Fehlschlag verbucht — sonst
sähe ein abgeschnittener Lauf wie ein schlechter Skill aus.

**Ein Trial ist eine Anekdote.** Triggering ist stochastisch; für eine belastbare
Aussage mehrere Trials fahren und mean±σ berichten, für Verlässlichkeitsaussagen
pass^k. Der Scorer bewertet einen Lauf — die Aggregation über N Läufe ist bewusst
nicht eingebaut — dafür gibt es eine dedizierte, generische Eval-Harness.
