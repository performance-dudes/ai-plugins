# tests/ocr/

Suite für das **ocr**-Plugin. **Einteilig** → code-nah `ocr/tests/validate.sh`;
Wrapper [`run.sh`](run.sh) für die Auto-Discovery.

## Was läuft (offline, ohne OCR-Engine/Netz/Modelle)
- **config-valid:** `plugin.json` parst, Komponenten vorhanden, Workflow-JS parst
  (`node --check`), Shell-Skripte `bash -n` + `+x`, Python-Skripte
  `py_compile`, Frontmatter der Commands/Skill.
- **unit (deterministisch):** `ocr.py` Session-Grouping (Scanner-Präfix),
  `anwenden.py` Dry-Run (Dokument→durchsuchbares PDF vs. Foto→Bild, **bewegt
  nichts**). Beides reine `python3`-Stdlib — kein Apple Vision/`auge`, kein
  PyMuPDF, kein Netz.

## Was übersprungen wird & warum
- **`claude plugin validate`** wenn `claude` fehlt — Skip-Note (guarded).
- **`node --check`** wenn `node` fehlt — Skip-Note.
- **Echtes OCR** (`auge`/Apple Vision, macOS 26, on-device) und die
  PDF-Text-Layer-Erzeugung (PyMuPDF) sowie der Opus-Klassifizierungs-Call sind
  **nicht** im Offline-Aggregat — externe Engine/Modelle/Cloud. Getestet wird die
  deterministische Logik darum herum.

## Nutzung
```bash
bash tests/ocr/run.sh           # nur dieses Plugin
bash ocr/tests/validate.sh      # identisch (code-nah)
```
Coverage: [`coverage.md`](coverage.md).
