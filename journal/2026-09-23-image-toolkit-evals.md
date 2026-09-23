# 2026-09-23 — `image-toolkit`: Knowledge-Eval-Suite und Qualitätsregel (0.2.1)

Schließt #63. Bei #62 war die fehlende Eval-Suite bewusst zurückgestellt worden.

## Suite

`plugins/image-toolkit/evals/`, Regime deterministisch: 25 gesperrte, geschlossene Fragen in
sechs Achsen (model, successor, size, param, engine, decline). Der Scorer liest `SKILL.md`
und alle `references/*.md` zur Laufzeit. Zertifiziert wird nach der Cold-Agent-Schleife aus
`plugin-eval`: frisches `claude -p` ohne Tools, Skills und MCP, `claude-sonnet-4-6`.

## Ergebnis

| Lauf | Accuracy | pass^k |
|---|---|---|
| mit Skill, 3 Trials | 1,00 ± 0,00 | 25/25 |
| Baseline ohne Skill | 0,28 | 7/25 |

Die Baseline lehnt alles ab, was sie nicht kennt. Richtig hat sie nur die Engine-Achse
(Allgemeinwissen) und die Decline-Achse (trivial, wenn man alles ablehnt). Beides steht
als Grenze in der Eval-README.

## Qualitätsregel in SKILL.md

Ohne `--size` rendert die API 1K. Damit ein Agent bei „finales Hero-Bild" oder „Druck"
nicht bei Entwurfsqualität landet, steht jetzt eine Tabelle in SKILL.md und im Command:
Entwurf 1K, Web/Social 2K, Druck 4K, höchste Qualität oder Text-lastig → Pro. Die
`size`- und `model`-Achse der Suite prüfen genau diese Regel.
