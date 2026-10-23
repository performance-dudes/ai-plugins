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
| Unicode-Textlayer (AC-OCR-4-4) | `searchbar.FONT_FILE`, `font_kwargs()` |
| `--redo` ersetzt unsichtbaren Layer (AC-OCR-4-5) | `searchbar.add_textlayer(replace=True)`, `pdf_has_only_invisible_text`, `durchsuchbar.py --redo` |

## spec : test (pro Typ)
| Aspekt | config-valid | unit | e2e |
|---|---|---|---|
| Session-Grouping korrekt | Syntax (`validate.sh`) | `validate.sh` §7 | — |
| Apply bewegt nichts im Dry-Run | — | `validate.sh` §8 | — |
| Foto-vs-Dokument-Schwelle | — | `validate.sh` §8 | echte Scans (manuell) |
| Textlayer-Font round-trip (Kyrillisch + Umlaute) | — | `validate.sh` §9 (macOS, sonst skipped) | — |
| `--redo`: Rotation, Kyrillisch, Links, Bild-Pixel; Abbruch bei leerem OCR, sichtbarem Text, Verschlüsselung, Text außerhalb der Seitenbox | — | `validate.sh` §10 (auge gemockt; macOS, sonst skipped) | 157 reale PDFs, manuell |
| `durchsuchbar.py --redo` CLI (Dry-Run, fehlender Pfad) | — | `validate.sh` §10 | — |
| echtes OCR/PDF-Layer | — | — | on-device, manuell (extern) |

## code : tests
| Komponente | config-valid | unit |
|---|---|---|
| `scripts/ocr.py` | `py_compile` | `session_key` |
| `scripts/anwenden.py` (+`searchbar.py`) | `py_compile` | Dry-Run-Plan, Font §9, `--redo` §10 |
| `scripts/durchsuchbar.py`, `klassifiziere.py` | `py_compile` | — |
| `scripts/doctor.sh` | `bash -n`, `+x` | — |
| `workflows/ocr.js` | Parse als async-Funktionskörper | — |
| `commands/*`, `skills/document-ocr/*` | Frontmatter | — |

## Lücken (Merge-Gate — schließen oder Issue)
- §9/§10 brauchen `uv` + macOS-`Helvetica.ttc`; der Linux-CI-Runner meldet sie als skipped — Issue #79.
- Abbruch bei signierten PDFs und bei geänderten Bilddaten ist offline nicht nachstellbar (kein Signier-Werkzeug, Redaction ändert Bilder nicht) — Issue #79.
- Kein E2E mit echter `auge`/PyMuPDF-Pipeline (extern: Apple Silicon + macOS 26).
  Bewusst offline ausgelassen; bei Bedarf Issue.
- Klassifizierungs-Prompt nur statisch (kein Opus-Call im Test).
