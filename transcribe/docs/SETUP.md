# Setup — transcribe plugin

One-time setup per machine. Run `/transcribe-doctor` any time to check status.

## Requirements

- **Apple Silicon Mac** — `mlx-whisper` is Metal/MLX only.
- **ffmpeg** — `brew install ffmpeg`
- **uv** — `brew install uv` (runs the Python scripts; pulls `mlx-whisper` and
  `pyannote.audio` automatically on first use via the PEP-723 headers)
- **node ≥ 20** — `brew install node` (the Workflow tool needs it; without node
  the `/transcribe` command falls back to a Bash-driven run)
- **claude CLI** — Claude Code, for the Opus deliverable step
- **HuggingFace token** — pyannote's `community-1` model is gated

## HuggingFace token (one-time)

pyannote needs a token to download `pyannote/speaker-diarization-community-1`.

1. Create a token at <https://huggingface.co/settings/tokens> (read scope).
2. Accept the model conditions on its HuggingFace page (once).
3. Store the token where the pipeline looks for it:

   ```bash
   mkdir -p ~/.cache/huggingface
   printf '%s' "<your-hf-token>" > ~/.cache/huggingface/token
   chmod 600 ~/.cache/huggingface/token
   ```

## First run

The first transcription downloads the models once: Whisper Large-v3-Turbo
(~3 GB) and pyannote community-1 (~0.5 GB). **Turn any VPN off** for that first
download — it otherwise tends to stall. Subsequent runs are fully offline for
phases 1–4.

## What goes where

- Audio and raw artifacts (`*.wav`, `*_whisper_turbo.json`, `*_diar.json`,
  `*_merged*`) stay next to the input audio.
- Deliverables land in `<stem>_transkript/` next to the audio.
- Nothing is uploaded except the transcript **text** sent to Opus for the
  deliverables — never the audio.
