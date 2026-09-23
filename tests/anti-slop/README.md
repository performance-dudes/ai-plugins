# tests/anti-slop

**Ablage: einteilig.** anti-slop ist ein reines Skill-Plugin ohne Build-Subprojekt,
also liegt die ganze Suite hier (SPEC-repo-conventions §5). Der Plugin-Ordner
bleibt damit reiner Runtime-Vertrag — bis auf `evals/`, das nach Repo-Praxis beim
Plugin liegt.

## Laufen lassen

```bash
bash tests/anti-slop/run.sh     # oder tests/run-all.sh (Auto-Discovery)
```

Offline. Die Tests brauchen nur `bash` und `python3`; die Eval am Ende braucht
zusätzlich PyYAML und läuft über `uv` (sonst `python3` mit PyYAML, sonst sichtbar
`SKIP`).

## Abgedeckte Typen

| Typ | Was |
|---|---|
| `config-valid` | Listen sind valides JSON im erwarteten Format, ohne Duplikate und ohne tote Einträge (auch keine Beschreibungen statt Suchstrings); `stock-name` ist nie hart, `stock-place` nie weich; SKILL.md-Frontmatter und Referenzlinks lösen auf. |
| `script-run` | `check-slop.py` gegen konstruierte Minimaltexte: Flexion, Literal-Abgrenzung, Satzzeichen-Ränder, Spracherkennung, Universal-Liste, Ladereihenfolge (Fixture), Entdoppelung überlappender Treffer, Exit-Codes. |
| `eval` | `evals/scripts/score_detection.py`: Trennschärfe zwischen generierter und menschlicher Prosa (US-slop-3), inklusive eines Cases, der nur über Flexion trifft. |

## Fixtures statt Echtdaten, wo die Echtdaten nichts beweisen

`AC-2-3` (die Universal-Liste gewinnt) und „hart vor lang" bei Überlappung laufen
gegen ein eigenes Datenverzeichnis (`ANTI_SLOP_DATA`). In den echten Listen steht
kein Term zugleich universal-weich und sprachlich-hart — dort hätte die
Ladereihenfolge keine beobachtbare Wirkung, und der Test könnte nicht rot werden.
In der Fixture entscheidet **nur** die Reihenfolge. Nachweis: `coverage.md`,
Mutationstabelle.
