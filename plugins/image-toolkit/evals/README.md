# evals — image-toolkit

Misst die **Qualität** des Skills, nicht seine Verdrahtung (das tut
`tests/validate.sh`).

## Was gemessen wird: Wissen, das ein Modell nicht mitbringt

Die Gemini-Bildmodelle wechseln schneller als jedes Trainingsdatum. Der Skill ist nur
dann etwas wert, wenn ein Agent **aus ihm allein** richtig entscheidet: welches Modell,
welche Auflösung, welche Parameter gehen, welcher Nachfolger für eine abgeschaltete ID,
Gemini oder ImageMagick. Genau das fragt die Suite ab.

| Achse | Fälle | Prüft |
|---|---|---|
| `model` | 5 | Modellwahl nach Anforderung (Default, Text-lastig, Masse, Qualität, Bild-Suche) |
| `successor` | 3 | abgeschaltete ID → GA-Nachfolger |
| `size` | 4 | `--size` nach Ziel (Entwurf, Web, Druck) und Modellgrenzen |
| `param` | 6 | Fähigkeiten je Modell, davon zwei Ja-Fälle gegen einen Immer-Nein-Bias |
| `engine` | 4 | Gemini, ImageMagick oder beides |
| `decline` | 3 | Fakten, die **nicht** im Skill stehen — erfinden ist der Fehler |

## Regime: deterministisch

Jede Frage ist geschlossen, die Antwort genau eine ihrer Optionen. `not-specified` ist
überall wählbar, damit Ablehnen immer möglich ist.

## Zertifizierung (plugin-eval, Cold-Agent-Schleife)

Ein **kalter**, **günstiger** Agent auf der Produktionsstufe (`claude-sonnet-4-6`), der
**nur** `SKILL.md` + `references/*.md` sieht, muss **100 %** beantworten — über alle
Trials (pass^k). Ein Baseline-Lauf **ohne** Skill muss deutlich scheitern, sonst misst die
Suite Vorwissen statt Skill.

## Das Objekt unter Test ist der echte Skill

`--emit-prompt` liest `skills/image-toolkit/SKILL.md` und alle Referenzen **zur Laufzeit**.
Es gibt keine Kopie im Harness.

## Cases sind locked

Ein Fehlschlag ist ein **Skill-Bug**: `SKILL.md` oder Referenz schärfen, nie den Case
aufweichen. Jeder `note` sagt, warum die Erwartung so lautet. Ändert Google Modelle oder
Grenzen, wird ein Case nur dann angepasst, wenn die **Wirklichkeit** sich geändert hat — mit
Quelle im Commit.

## Ausführen

```bash
python3 evals/scripts/score_knowledge.py --self-test   # ohne Modell, läuft in CI (validate.sh §8)
bash evals/run.sh                                      # 3 Trials + Baseline, ~1 Min.
TRIALS=5 MODEL=claude-sonnet-4-6 bash evals/run.sh
```

Der Runner startet je Trial ein frisches `claude -p` ohne Tools, Skills und MCP in einem
leeren Verzeichnis. Mit `ANTHROPIC_API_KEY` kommt `--bare` dazu (auch ohne CLAUDE.md und
Hooks).

## Grenzen

- Die `engine`-Achse besteht auch die Baseline: Gemini vs. ImageMagick ist Allgemeinwissen.
  Sie schützt vor Rückschritten im Skill, belegt aber kein Skill-Wissen.
- Die `decline`-Achse besteht eine Baseline, die alles ablehnt. Aussagekräftig ist sie
  **zusammen** mit den anderen Achsen: Der Skill-Lauf beantwortet 22 Fragen und lehnt
  genau die 3 ab, die nicht im Skill stehen.
- 25 Fälle fangen Regressionen, reichen aber nicht, um Modellvarianten zu ranken.
- Gemessen wird Wissen, nicht der Bild-Output. Ob ein generiertes Bild gut ist, prüft die
  Suite nicht (das kostete je Fall echte API-Aufrufe).
