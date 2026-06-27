# Spec: the `transcribe` plugin

**Theme:** Package the quality-first, on-device multi-speaker transcription flow
as a reusable, **generic** Claude Code plugin, so anyone on the team can run it
without re-deriving the pipeline — audio stays on-device, only transcript text
reaches the cloud, and all domain knowledge is supplied by the user, never shipped.

Hierarchy: **theme → user story (US) → acceptance criteria (AC) + test reference.**
Built following the PD plugin house style established by the `example` plugin.

---

## US-TR-1 — One command turns a recording into deliverables
> As a **team member**, I want to point the plugin at an audio file and get a
> verbatim speaker-labelled transcript plus minutes/facts/personas/todos, so that
> I don't have to wire the pipeline myself.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-TR-1-1 | `/transcribe <audio> [n]` and the `run-transcription` skill both invoke the single bundled `workflows/transcribe.js` by `scriptPath`. | review + `tests/validate.sh` (files present) |
| AC-TR-1-2 | The workflow runs phases 1–4 on-device, then produces `transkript_clean.md` + four deliverables in `<stem>_transkript/`. | review (workflow structure) |
| AC-TR-1-3 | The clean and deliverable passes are pinned to Opus. | review (`model: 'opus'` in workflow) |

## US-TR-2 — Generic: no customer/domain data shipped
> As a **maintainer**, I want the plugin to contain no names, companies or jargon,
> so it is safe to publish and works for any conversation.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-TR-2-1 | No proper nouns / customer terms in prompts or scripts; corrections come only from a user-provided CONTEXT block. | review (grep for names) |
| AC-TR-2-2 | The command and skill actively ask the user for context: language, speaker count, background, known names + their mis-transcriptions. | review (`commands/transcribe.md`, `SKILL.md`) |
| AC-TR-2-3 | An empty context still yields a faithful transcript (no guessed corrections). | review (workflow default context) |

## US-TR-3 — Every file valid, the chunker provably runnable
> As a **developer**, I want every shipped file validated and the deterministic
> chunker unit-tested, so the plugin is provably healthy without audio or models.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-TR-3-1 | `plugin.json` is valid JSON; `workflows/transcribe.js` passes `node --check`. | `tests/validate.sh` |
| AC-TR-3-2 | Every shell script has valid syntax and is executable; every Python script compiles. | `tests/validate.sh` |
| AC-TR-3-3 | `prepare_chunks.py` produces a correct manifest (turn counts, anchors, 85 % floor, speaker map) on a synthetic transcript. | `tests/validate.sh` (chunker unit test) |

## US-TR-4 — Honest about on-device vs cloud
> As a **privacy-conscious user**, I want it stated plainly what is processed where,
> so I can trust the tool with sensitive audio.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-TR-4-1 | README/SETUP state: audio never leaves the machine; only transcript text goes to Opus. | review |
| AC-TR-4-2 | `/transcribe-doctor` reports every dependency with a copy-paste fix and installs nothing. | review (`scripts/doctor.sh` exits 0, never installs) |
