---
description: Check that the transcription pipeline's dependencies are installed and configured
---

# /transcribe-doctor — preflight check

Verify the local environment can run the transcription pipeline. Run the bundled
check and present the result as a checklist, with the exact fix command for
anything missing. **Do not install anything automatically** — show the command
and let the user run it.

!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/doctor.sh`

Each line is `OK` or `MISS`/`FAIL` with a hint. Summarize what is ready and what
the user must install, with copy-paste fixes:

- **ffmpeg** → `brew install ffmpeg`
- **uv** → `brew install uv` (runs the Python scripts; pulls mlx-whisper / pyannote on first use)
- **node ≥ 20** → `brew install node` (the Workflow tool needs it; without it the command uses the Bash fallback)
- **HuggingFace token** → pyannote needs it; see https://github.com/performance-dudes/ai-plugins/blob/main/docs/transcribe/SETUP.md
- **claude CLI** → required for the Opus deliverable step

Note: `mlx-whisper` is Apple-Silicon only (Metal/MLX). On first run the models
(~3 GB Whisper, ~0.5 GB pyannote) download once — keep any VPN off for that.
