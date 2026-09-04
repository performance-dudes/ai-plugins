# Coverage — transcribe

Drei Achsen (SPEC-repo-conventions §6). Spec:
`specs/transcribe/0001_product_transcribe.md`. Typen: `config-valid` · `unit` · `e2e`.

## spec : code
| Spec-Aspekt | Code |
|---|---|
| On-device-Pipeline (ffmpeg→Whisper→pyannote) | `scripts/run_pipeline.sh`, `scripts/transcribe_whisper_mlx.py`, `scripts/diarize_pyannote.py`, `scripts/merge.py` |
| Chunking mit Ankern (Turn-Count, ≥85 %) | `scripts/prepare_chunks.py` |
| Speaker-Map | `scripts/prepare_chunks.py` (`--map`) |
| Verbatim-Clean + Quote-Pflicht (Deliverables) | `workflows/transcribe.js`, `skills/transcription/*` |

## spec : test (pro Typ)
| Aspekt | config-valid | unit | e2e |
|---|---|---|---|
| Chunker-Anker korrekt | Syntax (`validate.sh`) | `validate.sh` §7 | — |
| Speaker-Map angewandt | — | `validate.sh` §7 | — |
| Diarizer-Decoder FFmpeg-8-fest | `validate.sh` §8 (Regression) | — | — |
| echte Transkription | — | — | on-device, manuell (extern) |

## code : tests
| Komponente | config-valid | unit |
|---|---|---|
| `scripts/prepare_chunks.py` | `py_compile` | Chunker-Anker + Map |
| `scripts/diarize_pyannote.py` | `py_compile`, §8 Decoder-Pfad + Dep-Ban | — |
| `scripts/merge.py`, `transcribe_whisper_mlx.py` | `py_compile` | — |
| `scripts/run_pipeline.sh`, `doctor.sh` | `bash -n`, `+x` | — |
| `workflows/transcribe.js` | `node --check` | — |
| `commands/*`, `skills/transcription/*` | Frontmatter | — |

## Lücken (Merge-Gate — schließen oder Issue)
- Kein E2E der echten Audio-Pipeline (extern: ffmpeg/Whisper/pyannote, HF-Token,
  Apple Silicon). Bewusst offline ausgelassen; bei Bedarf Issue.
- Deliverable-Prompts nur statisch (kein Opus-Call im Test).
