# transcribe — plugin state

Current-state documentation for the `transcribe` plugin (intent lives in
`specs/transcribe/0001_product_transcribe.md`; the running log is in `journal/`).

## What it is

A quality-first, multi-speaker transcription plugin for Apple Silicon. Audio is
processed entirely on-device; only the transcript **text** is sent to Opus for
the deliverables. All domain knowledge is supplied by the user per conversation
(the CONTEXT block) — the plugin ships none.

## Architecture (when read / who triggers / where it runs)

| Component | File | Triggered by | Runs |
|-----------|------|--------------|------|
| Workflow | `transcribe/workflows/transcribe.js` | command or skill, by `scriptPath` | Workflow tool (orchestrates agents) |
| Command `/transcribe` | `transcribe/commands/transcribe.md` | user types it | main session |
| Command `/transcribe-doctor` | `transcribe/commands/transcribe-doctor.md` | user types it | main session (Bash) |
| Skill `run-transcription` | `transcribe/skills/transcription/SKILL.md` | model, on matching request | main session |
| Pipeline scripts | `transcribe/scripts/*` | the workflow / fallback, via Bash | on-device |

## Flow

```
/transcribe ─┐
             ├─▶ workflows/transcribe.js
skill      ──┘      │
                    ├─ Pipeline      run_pipeline.sh (ffmpeg→Whisper→pyannote) + merge.py  [on-device]
                    │                + propose speaker map from the first minutes
                    ├─ Chunk         prepare_chunks.py → chunk_NN.txt + manifest.json       [on-device]
                    ├─ Clean         parallel Opus, one strict verbatim pass per chunk → assemble
                    └─ Deliverables  parallel Opus: protokoll, fakten, personas, todos
                    └─▶ <stem>_transkript/{transkript_clean,protokoll,fakten_mit_zitaten,personas,todos}.md
```

## Quality contract

- **Verbatim clean transcript** via a strict anchored prompt: exact turn count,
  anchored first/last block, ≥85 % length floor, self-check. Opus only.
- **Quote obligation** on every fact / persona point / todo — no quote, no item.
- **On-device for audio**; cloud only for transcript text.

## Known limitations

- Multi-hour recordings can exceed a single Bash timeout during Whisper/pyannote;
  `run_pipeline.sh` is idempotent, so a re-run resumes.
- Speaker mapping is proposed automatically and meant to be reviewed; correct a
  wrong name with a re-run (`speakerMap: "SPEAKER_00=Name …"`).

## Tests

`bash transcribe/tests/validate.sh` — structure + syntax of every file, plus a
deterministic unit test of the chunker (no audio, no models).
