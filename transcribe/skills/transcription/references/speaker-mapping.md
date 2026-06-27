# Speaker mapping — diarization gotchas

pyannote labels speakers `SPEAKER_00`, `SPEAKER_01`, … in order of first
appearance. These IDs are arbitrary and must be mapped to real names before the
deliverables are produced.

## How to map

1. Read the first few minutes of `<stem>_merged.txt`.
2. Collect self-introductions ("Hi, I'm …", "Mein Name ist …") and match each
   `SPEAKER_NN` to a name.
3. Pass the mapping to `prepare_chunks.py --map SPEAKER_00=Name …`, or re-run the
   workflow with `speakerMap: "SPEAKER_00=Name …"`.

The workflow proposes a mapping automatically from the first minutes and returns
it; review it and correct any wrong name with a re-run.

## Gotchas

- **Always pass the known speaker count.** `run_pipeline.sh "<audio>" N`. Without
  it pyannote guesses and usually over-clusters. If unsure of the exact count,
  give a tight range and let it settle.
- **Over-splitting is the norm, not the exception.** One real person can be
  spread across several `SPEAKER_NN` clusters (changing mic distance, crosstalk).
  When two clusters are clearly the same voice, map both IDs to the same name.
- **Silent observers stay hidden** — someone who never speaks gets no cluster.
  That is correct, not a bug.
- **A speaker who never self-introduces** can't be named from content alone —
  map them to a neutral label (e.g. "Sprecher A") and let the user rename.
- **Plausibility over blind trust.** If a block's content clearly belongs to a
  different participant than the mapped name, mark it `(Name?)` rather than
  silently rewriting — flag, don't fabricate.
