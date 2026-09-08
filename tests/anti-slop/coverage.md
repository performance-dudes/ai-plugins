# anti-slop — Coverage-Matrix

Handgepflegt (SPEC-repo-conventions §10). Drei Achsen: spec:code · spec:test ·
code:test.

## spec : code

| AC | Komponente |
|---|---|
| AC-1-1 · AC-1-2 · AC-1-3 | `scripts/check-slop.py` → `pattern()` (Stamm-Suffix, Lookaround-Ränder) |
| AC-2-1 | `check-slop.py` → `detect()` |
| AC-2-2 · AC-2-3 | `check-slop.py` → `LISTS["universal"]`, Ladereihenfolge in `main()` |
| AC-3-1 · AC-3-2 · AC-3-3 | `evals/scripts/score_detection.py`, `data/severity-overrides.json` |
| AC-4-1 … AC-4-5 | `data/slop-list*.json` |
| AC-5-1 | `NOTICE` (Repo-Root) |
| AC-5-2 | `skills/anti-slop/SKILL.md` (Quellentabelle) |

## spec : test (pro Typ)

| AC | config-valid | script-run | eval |
|---|---|---|---|
| AC-1-1 | — | ✅ `run.sh` (Flexion, gemeldete Form) | — |
| AC-1-2 | — | ✅ `run.sh` (`murmelten` darf nicht, `murmelte` muss) | — |
| AC-1-3 | — | ✅ `run.sh` (`Selbstverständlich!`) | — |
| AC-2-1 | — | ✅ `run.sh` (de/en) | — |
| AC-2-2 | — | ✅ `run.sh` (`oaicite` in beiden Sprachen) | — |
| AC-2-3 | — | ✅ `run.sh` (`aria` hard/soft) | — |
| AC-3-1 | — | — | ✅ `score_detection.py` (h01–h04; h04 mit 268 Wörtern der dichteste Fall) |
| AC-3-2 | — | — | ✅ `score_detection.py` (g01–g04) |
| AC-3-3 | — | — | ✅ precision/recall/specificity |
| AC-4-1 | ✅ | — | — |
| AC-4-2 | ✅ | — | — |
| AC-4-3 | ✅ | — | — |
| AC-4-4 | ✅ | — | — |
| AC-4-5 | ✅ | — | — |
| AC-5-1 | ✅ | — | — |
| AC-5-2 | review | — | — |

## code : test (pro Typ)

| Komponente | config-valid | script-run | eval |
|---|---|---|---|
| `check-slop.py` | ✅ Syntax (`ast.parse`) | ✅ 11 Fälle | ✅ 9 Cases |
| `slop-list.json` | ✅ | indirekt | ✅ |
| `slop-list-en-extra.json` | ✅ | indirekt | ✅ |
| `slop-list-de.json` | ✅ | ✅ (Flexion, Satzzeichen) | ✅ |
| `slop-list-universal.json` | ✅ | ✅ (`oaicite`, `aria`) | indirekt |
| `severity-overrides.json` | ✅ Vorhandensein/Form | ✅ (`aria` weich) | ✅ (h02) |
| `SKILL.md` | ✅ Frontmatter + Links | — | — |
| `references/*.md` | ✅ Existenz | — | — |

## Mutationsnachweis

Ein grüner Test beweist nichts, solange nicht gezeigt ist, dass er rot werden
kann. Gemessen am 2026-09-08:

| Mutation | Suite | Eval |
|---|---|---|
| Ladereihenfolge umgedreht (`langs + ["universal"]`) | **FAIL** (AC-2-3) | — |
| `severity-overrides.json` gelöscht | **FAIL** | **FAIL** (h02: 75,5 / 1000) |
| `stock-place` auf `soft` gesetzt | **FAIL** (AC-4-5) | — |
| unverändert | PASS | PASS |

Der dritte Fall kam aus einem Fehler: Beim Beheben des ersten wurden dreizehn
erfundene Ortsnamen zusammen mit den Personennamen weich gesetzt, obwohl die
Begründung von AC-4-5 — „das sind auch reale Namen" — auf sie nicht zutrifft.
Eine Probe generierter englischer Fiktion fiel dadurch von 211 auf 0 harte
Treffer je 1000 Wörter. Orte stehen jetzt unter `stock-place` und bleiben hart;
der Eval-Case `g05-narrative-en` deckt die Lücke ab, in der das unsichtbar war.

Der erste Fall war zunächst **nicht** falsifizierbar: Die Upstream-Namen standen
nur in `slop-list.json` und wurden dort pauschal als hart gewertet, also hatte die
Reihenfolge keine beobachtbare Wirkung. Erst seit `slop-list-universal.json` diese
30 Namen als `soft` führt, misst AC-2-3 tatsächlich die Reihenfolge.

## Lücken

- **AC-5-1 prüft Anwesenheit, nicht Vollständigkeit.** Der Test greppt `NOTICE`
  nach den fünf Quellnamen — er wird rot, wenn jemand `NOTICE` leert, beweist aber
  nicht, dass jeder Term einer Quelle zugeordnet ist. Eine Herkunft je Term würde
  das leisten und ist bewusst nicht erhoben: die Listen führen Terme, keine
  Provenienz. Als Grenze benannt, nicht als Deckung ausgegeben.
- **AC-5-2** (SKILL.md nennt je Liste die Quelle) ist ein Review-Punkt, kein
  automatischer Test. Ein Test müsste Prosa gegen eine zweite Quellenliste
  prüfen — das wäre die gepflegte Zweitfassung, die das Repo gerade vermeidet.
- **Die deutschen Terme sind kuratiert, nicht gemessen.** Es gibt keine
  Frequenzdaten wie bei der englischen EQ-Bench-Liste, weil kein deutscher
  Vergleichskorpus öffentlich vorliegt. Als Issue zu tracken (SPEC §7).
