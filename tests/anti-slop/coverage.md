# anti-slop — Coverage-Matrix

Handgepflegt (SPEC-repo-conventions §6). Drei Achsen: spec:code · spec:test ·
code:test.

## spec : code

| AC | Komponente |
|---|---|
| AC-1-1 · AC-1-2 · AC-1-3 | `scripts/check-slop.py` → `pattern()` (Stamm-Suffix, Lookaround-Ränder) |
| AC-1-4 | `check-slop.py` → Entdoppelung in `main()` (hart vor lang, dann längster Treffer) |
| AC-1-5 | `check-slop.py` → `main()` (Lesefehler → Exit 2, Treffer → Exit 1) |
| AC-2-1 | `check-slop.py` → `detect()` |
| AC-2-2 · AC-2-3 | `check-slop.py` → `LISTS["universal"]`, Ladereihenfolge und Memo vor dem Filter in `main()` |
| AC-3-1 … AC-3-5 | `evals/scripts/score_detection.py`, `data/severity-overrides.json`, `data/slop-list*.json` |
| AC-4-1 … AC-4-5 | `data/slop-list*.json` |
| AC-4-6 | `data/severity-overrides.json` gegen `data/slop-list*.json` |

## spec : test (pro Typ)

| AC | config-valid | script-run | eval |
|---|---|---|---|
| AC-1-1 | — | ✅ `run.sh` (Flexion, gemeldete Form) | ✅ `g06-flexion-de` |
| AC-1-2 | — | ✅ `run.sh` (`murmelten` darf nicht, `murmelte` muss) | — |
| AC-1-3 | — | ✅ `run.sh` (`Selbstverständlich!`) | — |
| AC-1-4 | — | ✅ `run.sh` („is a testament to" = 1 Treffer; hart vor lang, Fixture) | — |
| AC-1-5 | — | ✅ `run.sh` (fehlende Datei, Nicht-UTF-8 → 2) | — |
| AC-2-1 | — | ✅ `run.sh` (de/en) | — |
| AC-2-2 | — | ✅ `run.sh` (`oaicite` in beiden Sprachen) | — |
| AC-2-3 | — | ✅ `run.sh` (Fixture: universal-weich gegen sprachlich-hart, mit Gegenprobe) | — |
| AC-3-1 | — | — | ✅ `score_detection.py` (h01–h04) |
| AC-3-2 | — | — | ✅ `score_detection.py` (g01–g06) |
| AC-3-3 | — | — | ✅ precision/recall/specificity |
| AC-3-4 | — | — | ✅ `score_detection.py` (h05-literary-en, h06-literary-de) |
| AC-3-5 | — | — | ✅ `g06-flexion-de` |
| AC-4-1 | ✅ | — | — |
| AC-4-2 | ✅ | — | — |
| AC-4-3 | ✅ (inkl. Beschreibungen statt Suchstrings) | — | — |
| AC-4-4 | ✅ | — | — |
| AC-4-5 | ✅ (`stock-name` nie hart, `stock-place` nie weich) | — | — |
| AC-4-6 | ✅ | — | — |

## code : test (pro Typ)

| Komponente | config-valid | script-run | eval |
|---|---|---|---|
| `check-slop.py` | ✅ Syntax (`ast.parse`) | ✅ 16 Fälle | ✅ 12 Cases |
| `slop-list-en-extra.json` | ✅ | ✅ (Überlappung) | ✅ |
| `slop-list-de.json` | ✅ | ✅ (Flexion, Satzzeichen) | ✅ |
| `slop-list-universal.json` | ✅ | ✅ (`oaicite`) | indirekt |
| `severity-overrides.json` | ✅ Vorhandensein, Form, Schlüssel treffen | ✅ (`aria` weich) | ✅ (h05, h06) |
| `SKILL.md` | ✅ Frontmatter + Links | — | — |
| `references/*.md` | ✅ Existenz | — | — |

## Mutationsnachweis

Ein grüner Test beweist nichts, solange nicht gezeigt ist, dass er rot werden
kann. Jede Mutation lief gegen die ganze Suite (`tests/anti-slop/run.sh`, inklusive
Eval) in einer Wegwerf-Kopie:

| Mutation | Suite | Rot durch |
|---|---|---|
| Ladereihenfolge umgedreht (`langs + ["universal"]`) | **FAIL** | AC-2-3 (Fixture) und seine Gegenprobe |
| Memo erst nach dem `--hard-only`-Filter | **FAIL** | AC-2-3 (Fixture) |
| Entdoppelung überlappender Treffer aus | **FAIL** | AC-1-4 („is a testament to") |
| „hart vor lang" aus (nur die Länge entscheidet) | **FAIL** | AC-1-4 (Fixture) |
| Flexion aus (`STEM_SUFFIX = ""`) | **FAIL** | AC-1-1; Eval `g06-flexion-de` 306 → 0,0 / 1000 |
| `severity-overrides.json` gelöscht | **FAIL** | AC-4-1; Eval h05 13,3 · h06 17,9 / 1000 |
| Register-Marker (`charming`, `äußerst`) aus den Overrides entfernt | **FAIL** | Eval h05 13,3 · h06 17,9 / 1000 |
| Override-Schlüssel ohne Listeneintrag (`vielfältig` statt `vielfältig*`) | **FAIL** | AC-4-6 |
| ein `stock-place` auf `soft` gesetzt | **FAIL** | AC-4-5 |
| Beschreibung statt Suchstring eingefügt (`"the x of y" formula`) | **FAIL** | AC-4-3 |
| unverändert | PASS | — |

## Lücken

- **Vollständigkeit der Listen ist nicht geprüft.** Der Test misst Format,
  Dublettenfreiheit und Severity-Regeln — nicht, ob ein Term fehlt. Die
  Trennschärfe misst stattdessen die Eval.
- **Die Terme sind kuratiert, nicht gemessen.** Die Severity ist ein redaktionelles
  Urteil (#61).
- **Die Eval-Stichprobe ist klein** (6 + 6 Cases) und bis auf h05/h06 selbst
  geschrieben; siehe `plugins/anti-slop/evals/README.md`.
