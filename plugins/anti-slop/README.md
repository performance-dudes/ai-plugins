# anti-slop

Removes the **machine tell** from prose — the words, phrases and cadences that
are statistically over-represented in generated text and make a draft read as
AI-written, whether or not it is. Two registers (business, narrative), two
languages (German, English), plus language-neutral artifacts.

Register the marketplace once, enable the plugin per project.

## Skill

| Skill | What it does |
|---|---|
| `anti-slop` | Names why a draft sounds generated, and replaces the slop with the concrete thing. Ships 1843 entries (1836 distinct) across three grep-checked lists plus a flexion-aware checker script. |

## Why a script and not a grep

German inflects. A `\b`-anchored search for `entscheidend` misses
`entscheidende`, `entscheidender`, `entscheidendes` — which is how the word
actually appears in a sentence. Run a plain grep of an English slop list over
German prose and it finds essentially nothing.

`scripts/check-slop.py` matches stem-plus-suffix for the German entries, detects
the language, and reports **hard hits per 1000 words** — the density, not any
single hit, is what decides.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/scripts/check-slop.py draft.md
```

## Hard versus soft

`tapestry` is a tell on its own. `zudem`, `nutzen` and `besonders` are ordinary
German words that only convict in clusters. Every curated term therefore carries
a severity, and `data/severity-overrides.json` demotes 71 of them to soft: code
collisions (`aria` matches every `aria-label`, and so do `transform`, `manifest`,
`key` and `harness`), ordinary English, and register markers that mark literary
or academic prose rather than machine prose (`profound`, `charming`, `anchor` ·
`mannigfaltig*`, `in der tat`, `äußerst`).

Two measurements. On 17 500 words of technical documentation: **5.5** hard hits
per 1000 words before the code-collision overrides, **0.5** after. On 1.04 million
words of literature published before 1926 — where every hard hit is a false
positive by construction — **0.0 to 0.2** hard hits per 1000 words, against
128–293 for generated text.

## The lists

| File | Terms |
|---|---|
| `slop-list-en-extra.json` | 1190 · curated English |
| `slop-list-de.json` | 496 · curated German |
| `slop-list-universal.json` | 157 · stock names and places, chatbot artifacts, placeholders |

No comparable public German list exists — `slop-list-de.json` was built for this
plugin.

## What it is not

- **Not an AI detector.** It judges prose, not authorship. A high score means
  "reads generically", not "written by a machine".
- **Not find-and-replace.** Every hit is a question. The fix is the specific
  fact, never a synonym.
- **Not an em-dash ban.** The em-dash is widely called an AI tell and is on no
  list here — that is a house-style question.

## Tests and evals

```bash
bash tests/anti-slop/run.sh                                    # wiring, offline
uv run plugins/anti-slop/evals/scripts/score_detection.py      # separation
```
