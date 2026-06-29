# transcribe — quality-first multi-speaker transcription

Audio in, deliverables out: a verbatim, speaker-labelled clean transcript plus
minutes, quoted facts, personas and todos. The audio is processed **entirely
on-device** (ffmpeg → Whisper → pyannote → merge); only the transcript **text**
is sent to Opus for the deliverables — never the audio.

```
ffmpeg ──▶ mlx-whisper ──▶ pyannote ──▶ merge ──▶ chunk ──▶ Opus deliverables
16k WAV    large-v3-turbo  community-1   speakers   windows   (parallel)
└──────────────── on-device ────────────────────┘           └─ cloud (text only) ─┘
```

## Generic by design

This plugin ships **no** domain knowledge — no names, no companies, no jargon.
Every name/term correction comes from a **CONTEXT block the user supplies per
conversation** (occasion, participants, proper nouns and their typical
mis-transcriptions, language). The command and skill ask for it; with no context
you still get a faithful transcript, just with the recognizer's raw spellings.

## Use it

```
/transcribe path/to/recording.m4a 5      # 5 = known speaker count (optional)
```

or just ask: *"transcribe this meeting recording"* — the `run-transcription`
skill triggers and gathers the context it needs.

Check your environment first:

```
/transcribe-doctor
```

## Components

| Component | Path | Shows |
|-----------|------|-------|
| Workflow | `workflows/transcribe.js` | orchestrates the pipeline + parallel Opus deliverables |
| Command | `commands/transcribe.md` | `/transcribe` → gathers context, invokes the workflow |
| Command | `commands/transcribe-doctor.md` | `/transcribe-doctor` → dependency preflight |
| Skill | `skills/transcription/SKILL.md` | autonomous trigger → same workflow |
| Scripts | `scripts/` | the on-device pipeline (`run_pipeline.sh`, `merge.py`, `prepare_chunks.py`, …) |

## Why Opus, always

The strict verbatim clean pass (complete, exact turn count, anchored start/end,
≥85 % length) needs Opus — Sonnet compresses long transcripts even under a strict
prompt. The workflow pins the clean and deliverable passes to Opus.

## Setup & testing

- Setup: [`docs/transcribe/SETUP.md`](../docs/transcribe/SETUP.md) (liegt im Marketplace-Repo, außerhalb des Plugin-Ordners — Repo-Konvention)
- Smoke test: `bash transcribe/tests/validate.sh`

Quality over speed: a slower, complete, faithful transcript beats a fast,
compressed one.
