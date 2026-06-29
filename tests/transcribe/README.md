# tests/transcribe/

Suite für das **transcribe**-Plugin. **Einteilig** → code-nah
`transcribe/tests/validate.sh`; Wrapper [`run.sh`](run.sh) für die Auto-Discovery.

## Was läuft (offline, ohne Audio/Netz/Modelle)
- **config-valid:** `plugin.json` parst, Komponenten vorhanden, Workflow-JS parst
  (`node --check`), Shell-Skripte `bash -n` + `+x`, Python-Skripte `py_compile`,
  Frontmatter der Commands/Skill.
- **unit (deterministisch):** `prepare_chunks.py` Chunker gegen ein synthetisches
  Transcript — Manifest-Anker (Turn-Count, erster Sprecher/Timestamp, ≥85 %-Floor,
  ≥2 Chunks bei Mini-Budget) und Speaker-Map-Anwendung. Reine `python3`-Stdlib
  (`uv` wird genutzt falls vorhanden, sonst `python3`-Fallback).

## Was übersprungen wird & warum
- **`claude plugin validate`** wenn `claude` fehlt — Skip-Note (guarded).
- **`node --check`** wenn `node` fehlt — Skip-Note.
- **Echte Pipeline** (`ffmpeg`→Whisper-MLX→`pyannote`, on-device) und die
  Opus-Deliverables sind **nicht** im Offline-Aggregat — externe Werkzeuge/Modelle
  (HuggingFace-Token, Apple Silicon) und Cloud. Getestet wird der deterministische
  Chunker dazwischen.

## Nutzung
```bash
bash tests/transcribe/run.sh          # nur dieses Plugin
bash transcribe/tests/validate.sh     # identisch (code-nah)
```
Coverage: [`coverage.md`](coverage.md).
