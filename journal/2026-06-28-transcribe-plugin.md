# 2026-06-28 — transcribe plugin

A reusable, generic packaging of the on-device multi-speaker transcription flow
(previously a local-only personal pipeline) as a public `ai-plugins` plugin,
following the `example` plugin's house style.

## What was done

- Vendored the deterministic pipeline scripts verbatim (`run_pipeline.sh`,
  `transcribe_whisper_mlx.py`, `diarize_pyannote.py`, `merge.py`) and added a new
  deterministic `prepare_chunks.py` (context-sized chunking + anchor manifest) and
  a `doctor.sh` preflight.
- Wrote `workflows/transcribe.js`: Pipeline → Chunk → parallel Opus clean passes
  → assemble → parallel Opus deliverables. Command and skill both invoke it by
  `scriptPath` (single source of truth), with a Bash fallback.
- Added the PD structure: `specs/transcribe/0001_product_transcribe.md` (US/AC), `docs/transcribe.md`
  (state), a per-plugin `tests/validate.sh` with a real chunker unit test.

## Decisions & learnings

- **Generic, no customer data.** The original strict clean-transcript prompt
  carried customer-specific name corrections (a real meeting's proper nouns).
  Those were stripped entirely; corrections now come only from a user-supplied
  CONTEXT block. The command and skill actively ask the user for language,
  speaker count, background and known names + their mis-transcriptions.
- **Workflow over inline command bash.** The deliverables were 8 sequential Opus
  calls in the old pipeline; the workflow fans them out in parallel — faster and
  the canonical PD wiring. Named-workflow resolution does not discover plugin
  scripts, so the command/skill invoke `${CLAUDE_PLUGIN_ROOT}/workflows/transcribe.js`
  by path.
- **Opus pinned.** Empirically Sonnet compresses long transcripts even under a
  strict prompt; the clean and deliverable passes are pinned to Opus.
- **Speaker mapping can't gate a background workflow.** Instead of a mid-run human
  checkpoint, the workflow proposes a map from self-introductions and returns it
  for review; a wrong name is fixed with a re-run.
- **Open limitation.** Multi-hour audio can exceed a single Bash timeout in the
  pipeline phase; mitigated by `run_pipeline.sh` being idempotent (re-run resumes).
  A future iteration could background the long phase and poll.
