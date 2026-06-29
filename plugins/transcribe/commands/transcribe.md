---
description: Transcribe an audio/video file into a verbatim clean transcript with speakers, plus minutes, quoted facts, personas and todos
argument-hint: "[audio-path] [num-speakers]"
---

# /transcribe — quality-first multi-speaker transcription

Run the plugin's bundled transcription workflow for `$ARGUMENTS`.

## Step 1 — gather CONTEXT (the biggest quality lever)

This plugin ships **no** domain knowledge — name and term corrections come
entirely from context **you** provide. Before running, make sure you have the
following, and **ask the user** for anything missing:

- **Audio path** — the file to transcribe (first argument).
- **Language / locale** of the conversation (e.g. `de-DE`, `en-US`). Default `de-DE`.
- **Number of speakers** if known (second argument) — improves diarization a lot.
- **Background / occasion** — what conversation is this, who are the participants
  (role, who tends to talk about what).
- **Known proper nouns & domain terms** plus their typical mis-transcriptions —
  e.g. a product, company or person name and how the recognizer tends to garble it.

Assemble these into a single CONTEXT block (plain text). If the user has nothing
to add, proceed with an empty context — the transcript is still produced, just
with fewer name corrections.

## Step 2 — run the workflow

**Preferred — Workflow orchestration.** If the **Workflow tool** is available,
invoke the bundled script. `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin's
install directory regardless of where it was installed:

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/transcribe.js",
  args: {
    pluginRoot: "${CLAUDE_PLUGIN_ROOT}",
    audio: "<audio path>",
    numSpeakers: "<count or empty>",
    locale: "<locale>",
    context: "<the CONTEXT block you assembled>"
  }
})
```

The workflow runs the on-device pipeline (ffmpeg → Whisper → pyannote → merge),
proposes a speaker mapping from the first minutes, then produces the verbatim
clean transcript and the deliverables with **Opus in parallel**.

When the task-notification arrives, report to the user:
- the **output directory** and the files produced,
- the **proposed speaker mapping** — and offer to re-run with corrections by
  passing `speakerMap: "SPEAKER_00=Name SPEAKER_01=Name"` in `args` if a name is wrong.

**Fallback (no Workflow tool).** Run the bundled scripts yourself via Bash, in
order: `run_pipeline.sh` → `merge.py` → propose a speaker map from the first
minutes → `prepare_chunks.py` → for **each** chunk produce a strict verbatim
clean transcript **with Opus** → assemble them → produce the five deliverables.
Full step-by-step: `${CLAUDE_PLUGIN_ROOT}/skills/transcription/references/pipeline.md`.

## Prerequisites

Everything runs on-device; only the Opus deliverable step uses the cloud (the
transcript text, never the audio). If a step fails to run, point the user to
`/transcribe-doctor`.
