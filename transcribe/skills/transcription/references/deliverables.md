# Deliverables — the five outputs and the context block

All deliverables land in `<stem>_transkript/` next to the audio.

| File | What it is |
|------|------------|
| `transkript_clean.md` | Verbatim, speaker-labelled clean transcript (the base for everything else). Produced per chunk with a strict anchored prompt, then concatenated. |
| `protokoll.md` | Sober minutes — participants & occasion, chronological course, key facts & decisions, commitments / next steps. |
| `fakten_mit_zitaten.md` | Key facts, **each backed by a verbatim quote** `[HH:MM:SS] Speaker: "…"`. No quote → fact dropped. |
| `personas.md` | A short profile per named person — role/company, what was said about them (quote-backed), relation to participants. |
| `todos.md` | Explicit commitments and open points — who, what, by when, with a quote. |

## The CONTEXT block — generic, user-supplied

The plugin ships **no** names or domain terms. The single biggest quality lever
is the CONTEXT the user provides per conversation. A good context block names:

- the occasion and participants (role, who talks about what),
- proper nouns and domain terms **with their typical mis-transcriptions**
  (e.g. "the recognizer tends to write X when the speaker means Y"),
- the conversation language / locale.

The clean-transcript pass corrects garbled names **only** from this context — it
never guesses a correction it has no basis for. With no context it still produces
a faithful transcript, just with the recognizer's original spellings.

## The quote obligation

Every fact, persona point and todo must carry a verbatim `[HH:MM:SS] Speaker:
"quote"`. No matching quote → the item is omitted. This is the strongest
anti-hallucination guardrail in the pipeline — keep it strict.

## Why Opus, never Sonnet

Empirically, Sonnet compresses long transcripts to a fraction of their length
even under a strict prompt; only Opus holds the verbatim, exact-turn-count,
length-floor contract. The workflow pins the clean and deliverable passes to
Opus for this reason.
