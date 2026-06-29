---
name: run-transcription
description: Transcribe an audio or video recording into a verbatim, speaker-labelled clean transcript plus deliverables (minutes, quoted facts, personas, todos) using the plugin's bundled on-device pipeline and parallel Opus passes. Use when the user wants to transcribe a meeting/interview/workshop recording, asks for speaker diarization, a clean transcript, or meeting minutes/facts/todos from audio. Trigger phrases — "transcribe this", "transcribe the recording", "transkribiere", "clean transcript", "speaker diarization", "who said what", "meeting minutes from audio", "protokoll aus aufnahme".
argument-hint: "[audio-path] [num-speakers]"
---

# run-transcription — call the bundled transcription workflow

This skill lets the model start the transcription pipeline autonomously when a
request matches, without the user remembering the `/transcribe` command. Both
funnel into the **same** `workflows/transcribe.js` — single source of truth.

## This plugin is generic — context comes from the user

It ships **no** domain knowledge. Name/term corrections come entirely from
context the user gives. Before running, gather and (if missing) **ask for**:

1. **Audio path** — the recording to transcribe.
2. **Language / locale** (e.g. `de-DE`, `en-US`; default `de-DE`).
3. **Number of speakers** if known — improves diarization markedly.
4. **Background / occasion** — what conversation, which participants, who talks
   about what.
5. **Known proper nouns & domain terms** + their typical mis-transcriptions.

Assemble these into one plain-text CONTEXT block. Empty context is allowed (the
transcript is still produced, with fewer corrections) — but a rich context is
the single biggest quality lever, so prefer to ask.

## What to do

1. Resolve the audio path and the context above.

2. If the **Workflow tool is available**, run the bundled script.
   `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin's install directory:

   ```
   Workflow({
     scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/transcribe.js",
     args: {
       pluginRoot: "${CLAUDE_PLUGIN_ROOT}",
       audio: "<audio path>",
       numSpeakers: "<count or empty>",
       locale: "<locale>",
       context: "<the CONTEXT block>"
     }
   })
   ```

   It runs the on-device pipeline, proposes a speaker mapping, then produces the
   clean transcript and deliverables with Opus in parallel. When it returns,
   report the output directory, the files, and the **proposed speaker mapping** —
   offer a re-run with `speakerMap: "SPEAKER_00=Name ..."` if a name is wrong.

3. If the **Workflow tool is NOT available**, fall back to running the bundled
   scripts via Bash, in order — see
   `${CLAUDE_PLUGIN_ROOT}/skills/transcription/references/pipeline.md`.

## Quality-first principles

- **On-device for audio.** ffmpeg → Whisper → pyannote → merge never leave the
  machine. Only the deliverable text goes to Opus — never the audio.
- **Opus for the clean transcript, always.** Sonnet compresses long transcripts;
  the strict verbatim pass needs Opus. The workflow enforces this.
- **Quality over speed.** A slower, complete, faithful transcript beats a fast,
  compressed one.

References: `references/pipeline.md` (phases & script interfaces),
`references/speaker-mapping.md` (diarization gotchas),
`references/deliverables.md` (the five outputs and the context block).
