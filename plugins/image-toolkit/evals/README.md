# evals — image-toolkit

Misst die **Qualität** des Skills, nicht seine Verdrahtung (das tut
`tests/validate.sh`).

## Was gemessen wird: Wissen, das ein Modell nicht mitbringt

Die Gemini-Bildmodelle wechseln schneller als jedes Trainingsdatum. Der Skill ist nur
dann etwas wert, wenn ein Agent **aus ihm allein** richtig entscheidet: welches Modell,
welche Auflösung, welche Parameter gehen, welcher Nachfolger für eine abgeschaltete ID,
Gemini oder ImageMagick — und wie der vollständige Aufruf aussieht.

| Achse | Fälle | Prüft |
|---|---|---|
| `model` | 5 | Modellwahl nach Anforderung (Default, Text-lastig, Masse, Qualität, Bild-Suche) |
| `successor` | 3 | abgeschaltete ID → GA-Nachfolger |
| `size` | 4 | `--size` nach Ziel (Entwurf, Web, Großdruck) und Modellgrenzen |
| `param` | 6 | Fähigkeiten je Modell, davon zwei Ja-Fälle gegen einen Immer-Nein-Bias |
| `recent` | 13 | Fakten jünger als jedes Trainingsdatum: API-Route, Preise, Daten, Pixelmaße, Felder |
| `command` | 2 | vollständiger `generate_image.py`-Aufruf — echte Flags **und** `--size` nach Ziel |
| `engine` | 4 | Gemini, ImageMagick oder beides |
| `decline` | 4 | Fakten, die Google dokumentiert, der Skill aber auslässt — erfinden ist der Fehler |

## Regime: deterministisch

Geschlossene Fragen: Die Antwort ist genau eine Option. `command`-Fragen: Die Antwort ist
ein Aufruf, geprüft per Regex (`--prompt`, `--aspect`, `--size` mit dem richtigen Wert, kein
erfundenes `--aspect-ratio`). Kein Judge, keine Judge-Varianz.

## Zertifizierung (plugin-eval, Cold-Agent-Schleife)

- **Kalt:** frisches `claude -p` je Trial, leeres Verzeichnis, `--tools ""`,
  `--disable-slash-commands`, `--strict-mcp-config`, `--setting-sources ""`, eigener
  Einzeiler-System-Prompt. Gemessen: **~460 Input-Tokens** Kontext vor der Aufgabe (ein
  Standard-`claude -p` auf derselben Maschine lädt ~740k). Kein CLAUDE.md, kein Memory, keine
  Hooks, keine Plugins.
- **Günstig:** `claude-sonnet-4-6`, die Produktionsstufe.
- **Nur der Skill:** `SKILL.md` + `references/*.md`, zur Laufzeit eingelesen.
- **100 %:** jeder Fall in jedem Trial (pass^k).

## Baseline: Wahlzwang, sonst misst sie Zurückhaltung

Die Baseline sieht den Skill nicht und **muss** außerhalb der `decline`-Achse eine inhaltliche
Option wählen. Darf sie `not-specified` wählen, lehnt sie alles ab, was sie nicht sicher weiß,
und misst Zurückhaltung statt Wissen (so gemessen: 0,28 mit Ablehnoption gegen 0,72 mit
Wahlzwang, auf einer früheren Fassung der Suite).

Ein Fall ist **trennscharf**, wenn der Skill-Lauf ihn in jedem Trial besteht und die Baseline
nicht. Antwortoptionen sind so gebaut, dass Extremwerte und Namensmuster nicht verraten, welche
stimmt (alle Daten plausibel, alle Preise im selben Band, `previous_response_id` als
OpenAI-Köder).

## Ergebnis

| Lauf | Accuracy | pass^k |
|---|---|---|
| mit Skill, 3 Trials | 1,00 ± 0,00 | **41/41** |
| Baseline, Wahlzwang | 0,54 | — |
| trennscharf | | **19/41** |

Umgebung: Claude Code 2.1.280, `claude-sonnet-4-6`, Isolation wie oben.

## Schranken (`run.sh` scheitert mit Exit 1)

- **nicht zertifiziert** — ein Fall in einem Trial falsch.
- **Baseline > 0,65** — gemessen 0,54. Zufall läge bei ~0,3; `engine` (4) und `decline` (4)
  besteht die Baseline prinzipbedingt, das allein sind 0,2.
- **< 15 trennscharfe Fälle** — gemessen 19. Fällt die Zahl, sind Fälle zu leicht geworden
  oder der Skill trägt weniger Wissen, als die Suite behauptet.

Beide Schranken sind Regressionsschutz mit Abstand zum Messwert, keine Ranking-Grenze.

## Das Objekt unter Test ist der echte Skill

`--emit-prompt` liest `skills/image-toolkit/SKILL.md` und alle Referenzen **zur Laufzeit**.
Es gibt keine Kopie im Harness.

## Cases sind locked

Ein Fehlschlag ist ein **Skill-Bug**: `SKILL.md` oder Referenz schärfen, nie den Case
aufweichen. Jeder `note` sagt, warum die Erwartung so lautet. Ändert Google Modelle oder
Grenzen, wird ein Case nur angepasst, wenn die **Wirklichkeit** sich geändert hat — mit
Quelle im Commit.

## Ausführen

```bash
python3 evals/scripts/score_knowledge.py --self-test   # ohne Modell, läuft in CI (validate.sh §8)
bash evals/run.sh                                      # 3 Trials + Baseline, ~1 Min., Exit 0/1
TRIALS=5 bash evals/run.sh
```

Der Selbsttest prüft auch den Scorer: Abkürzungs-Antwortmuster (immer `not-specified`, immer
erste Option, immer „no") fallen durch, ein Aufruf ohne `--size` oder mit `--aspect-ratio`
besteht nicht, sieben Ausgabeformate werden erkannt.

## Grenzen

- `engine` und `decline` trennen nicht von der Baseline (Allgemeinwissen bzw. Ablehnen).
  Sie schützen vor Rückschritten im Skill.
- Die `recent`-Fälle sind Faktenwissen (Preise, Daten). Das ist gewollt — genau dieses Wissen
  fehlt einem Modell —, veraltet aber mit Googles Preisliste. Dann Case **und** Skill mit
  Quelle nachziehen.
- 41 Fälle fangen Regressionen, reichen aber nicht, um Modellvarianten zu ranken.
- Gemessen wird Wissen, nicht der Bild-Output. Ob ein generiertes Bild gut ist, prüft die
  Suite nicht (das kostete je Fall echte API-Aufrufe).
