# tests/anti-slop

**Ablage: einteilig.** anti-slop ist ein reines Skill-Plugin ohne Build-Subprojekt,
also liegt die ganze Suite hier (SPEC-repo-conventions §5). Der Plugin-Ordner
bleibt damit reiner Runtime-Vertrag — bis auf `evals/`, das nach Repo-Praxis beim
Plugin liegt.

## Laufen lassen

```bash
bash tests/anti-slop/run.sh     # oder tests/run-all.sh (Auto-Discovery)
```

Offline, zero-dep: nur `bash` und `python3`. Keine Netzzugriffe, keine Pakete.

## Abgedeckte Typen

| Typ | Was |
|---|---|
| `config-valid` | Listen sind valides JSON im erwarteten Format, ohne Duplikate und ohne tote Einträge; `stock-name` ist nie hart; SKILL.md-Frontmatter und Referenzlinks lösen auf; `NOTICE` nennt jede Fremdquelle. |
| `script-run` | `check-slop.py` gegen konstruierte Minimaltexte: Flexion, Literal-Abgrenzung, Satzzeichen-Ränder, Spracherkennung, Universal-Liste, Ladereihenfolge. |

## Was hier NICHT geprüft wird

Die **Trennschärfe** (US-slop-3) — also ob der Prüfer echten Slop von echter
Prosa trennt — misst die Eval, nicht dieser Test:

```bash
uv run plugins/anti-slop/evals/scripts/score_detection.py
```

Grund: Trennschärfe ist eine Qualitätsaussage über bekannte Inputs mit
festgezurrter Ground-Truth. Das ist der Measure-Schritt, nicht die Frage „ist es
korrekt verdrahtet". Die Eval braucht `uv` und bleibt deshalb aus der
zero-dep-Suite heraus.

## Der Test, der am ehesten rot wird

`AC-2-3` prüft, dass der Stock-Name `aria` **nicht** unter `--hard-only`
erscheint. `aria` steht in der Upstream-Liste, die pauschal als hart gilt, und in
`slop-list-universal.json` als `soft` — weich bleibt er also nur, solange die
Universal-Liste **zuerst** geladen wird. Dreht man die Reihenfolge um, geht dieser
Check rot (nachgewiesen, siehe `coverage.md`), und `aria` trifft wieder jedes
`aria-label` in technischer Doku.

Bis zum Cold-Review war dieser Test **nicht** falsifizierbar: die Upstream-Namen
fehlten in der Universal-Liste, `aria` wurde allein durch
`severity-overrides.json` entschärft, und die Ladereihenfolge hatte gar keine
beobachtbare Wirkung. Der Test war grün und maß das Falsche.
