# Pipeline reference — phases & script interfaces

The pipeline has five phases. Phases 1–4 are deterministic and on-device;
phase 5 (deliverables) is the only cloud step and uses Opus on the **text**.

```
ffmpeg ──▶ mlx-whisper ──▶ pyannote ──▶ merge ──▶ chunk ──▶ Opus deliverables
16k WAV    large-v3-turbo  community-1   speakers   windows   (parallel)
└──────────────── on-device ────────────────────┘           └─ cloud (text only) ─┘
```

All scripts live in `${CLAUDE_PLUGIN_ROOT}/scripts/`. Python scripts carry a
PEP-723 header, so run them with `uv run`.

## Phase 1–3 — `run_pipeline.sh`

```bash
bash run_pipeline.sh "<audio>" [num-speakers]
```

Produces, next to the audio:
- `<stem>.wav` — 16 kHz mono PCM
- `<stem>_whisper_turbo.json` — Whisper Large-v3-Turbo full text (word-level)
- `<stem>_yap.json` — symlink to the whisper json (merge.py input)
- `<stem>_diar.json` — pyannote community-1 speaker segments

Idempotent: it skips a phase whose output is newer than its input, so a
re-run resumes. Pass the **known speaker count** whenever you have it.

## Phase 4 — `merge.py`

```bash
uv run merge.py "<stem>"           # <stem> = audio path without extension
```

Mechanically merges transcript × speaker segments into:
- `<stem>_merged_raw.json` — list of `{start, end, speaker, text}` blocks
- `<stem>_merged.txt` — human-readable `[HH:MM:SS] SPEAKER_NN: text`

Run it **without** `--map` first; decide the speaker mapping by reading the
first minutes of `_merged.txt` (self-introductions). It also strips known
end-of-audio hallucination loops.

## Phase 4.5 — `prepare_chunks.py`

```bash
uv run prepare_chunks.py "<stem>_merged_raw.json" \
  --map SPEAKER_00=Name SPEAKER_01=Name \
  --out "<stem>_transkript"
```

Applies the speaker map, splits the transcript into context-sized windows
(default 60 000 chars, never splitting a block), and writes
`<out>/chunks/chunk_NN.txt` plus `<out>/chunks/manifest.json`. The manifest
carries the **anchors** each strict clean pass needs: `turn_count`,
`first_ts/first_speaker`, `last_ts/last_speaker`, `input_chars`,
`min_output_chars` (85 % floor).

## Phase 5 — deliverables (Opus, parallel)

For **each** chunk, an Opus agent produces a strict verbatim clean transcript
(complete, exact turn count, anchored start/end, ≥85 % length). The cleaned
chunks are concatenated into `transkript_clean.md`, and then five deliverables
are produced from it — see `deliverables.md`.

The `workflows/transcribe.js` script wires all of this together. The manual
fallback runs the same steps by hand when the Workflow tool is unavailable.

## Known limitation — very long audio

A single Bash invocation can time out on multi-hour recordings during Whisper/
pyannote. Because `run_pipeline.sh` is idempotent, simply re-run it — it resumes
from the last completed phase.
