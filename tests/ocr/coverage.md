# Coverage — ocr

Drei Achsen (SPEC-repo-conventions §6). Spec: `specs/ocr/0001_product_ocr.md`.
Typen: `config-valid` · `unit` · `e2e`.

## spec : code
| Spec-Aspekt | Code |
|---|---|
| On-device-OCR + Session-Grouping | `scripts/ocr.py` |
| Klassifizierung (generisch, user-CONTEXT) | `scripts/klassifiziere.py`, `scripts/classify_prompt.md`, `workflows/ocr.js` |
| Propose→review→apply, Dry-Run, Undo | `scripts/anwenden.py` |
| Durchsuchbare PDFs / Foto-vs-Dokument | `scripts/durchsuchbar.py`, `scripts/searchbar.py` |

## spec : test (pro Typ)
| Aspekt | config-valid | unit | e2e |
|---|---|---|---|
| Session-Grouping korrekt | Syntax (`validate.sh`) | `validate.sh` §7 | — |
| Apply bewegt nichts im Dry-Run | — | `validate.sh` §8 | — |
| Foto-vs-Dokument-Schwelle | — | `validate.sh` §8 | echte Scans (manuell) |
| echtes OCR/PDF-Layer | — | — | on-device, manuell (extern) |

## code : tests
| Komponente | config-valid | unit |
|---|---|---|
| `scripts/ocr.py` | `py_compile` | `session_key` |
| `scripts/anwenden.py` (+`searchbar.py`) | `py_compile` | Dry-Run-Plan |
| `scripts/durchsuchbar.py`, `klassifiziere.py` | `py_compile` | — |
| `scripts/doctor.sh` | `bash -n`, `+x` | — |
| `workflows/ocr.js` | `node --check` | — |
| `commands/*`, `skills/document-ocr/*` | Frontmatter | — |

## Lücken (Merge-Gate — schließen oder Issue)
- Kein E2E mit echter `auge`/PyMuPDF-Pipeline (extern: Apple Silicon + macOS 26).
  Bewusst offline ausgelassen; bei Bedarf Issue.
- Klassifizierungs-Prompt nur statisch (kein Opus-Call im Test).
