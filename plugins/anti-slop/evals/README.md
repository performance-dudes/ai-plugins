# anti-slop — evals

Misst die **Kern-Promise** des Plugins: schlägt der Prüfer auf generiertem Text
an und lässt er von Menschen geschriebene Prosa in Ruhe?

## Regime: deterministisch, kein Judge

Das beobachtbare Ergebnis ist eine Zahl — harte Treffer je 1000 Wörter. Das ist
objektiv, also wird **deterministisch gematcht** (repo-CLAUDE.md: STRUCTURED →
deterministisch). Ein LLM-Judge würde hier nur Varianz auf etwas legen, das schon
eindeutig ist.

## Das reale Objekt, nicht eine Kopie

`score_detection.py` ruft das ausgelieferte
`skills/anti-slop/scripts/check-slop.py` gegen die ausgelieferten Listen. In
`cases.yaml` steht **kein einziger** Term — ändert sich das Plugin, ändert sich
automatisch, was gemessen wird.

## Laufen lassen

```bash
uv run plugins/anti-slop/evals/scripts/score_detection.py
uv run plugins/anti-slop/evals/scripts/score_detection.py --json
```

`uv` zieht PyYAML über den PEP-723-Header; eine Installation ist nicht nötig.

## Schwellen (aus SPEC-anti-slop US-slop-3)

| origin | Schwelle | Warum |
|---|---|---|
| `human` | **≤ 1,0** harte Treffer / 1000 Wörter | Ein Prüfer, der auf normaler Fachprosa anschlägt, wird überlesen. |
| `generated` | **≥ 50,0** harte Treffer / 1000 Wörter | Der Abstand zwischen beiden Grenzen ist das Versprechen des Plugins. |

Der Zwischenraum ist **kein** Toleranzband. Landet ein Case dort, ist das ein
Befund am Plugin, keine Einladung, die Schwelle zu verschieben.

## Die Cases sind eingefroren

Ein Fehlschlag ist ein **Plugin-Bug** — gefixt werden Listen, Overrides oder
Skript. Ein Case wird nie aufgeweicht, umformuliert oder gelöscht, damit der Run
grün wird.

Die `note` an jedem Case ist der Kalibrier-Anker: sie sagt, *warum* der Case so
aussieht. `h02-technical-en` etwa benutzt bewusst `key`, `transform`, `harness`,
`manifest` und `dynamic` — genau die Wörter, die `severity-overrides.json`
herabstuft. Fällt die Override-Datei weg, geht dieser Case als Erster rot.

`h03` und `g04` beschreiben dieselbe Szene, einmal geschrieben und einmal
generiert. Das trennt Erzähl-Slop von Erzählung.

## Kennzahlen

`precision` (gemeldeter Slop, der wirklich Slop ist) · `recall` (erkannter Anteil
des echten Slops) · `specificity` (Menschentext, der in Ruhe gelassen wird) ·
`separation` (Abstand zwischen dem leisesten generierten und dem lautesten
menschlichen Text).

Stand: 9 Cases, precision/recall/specificity je 1,0, kein einziger Treffer auf
Menschentext.
