# anti-slop

Removes the **machine tell** from prose — the words, phrases and cadences that
are statistically over-represented in generated text and make a draft read as
AI-written, whether or not it is. Two registers (business, narrative), two
languages (German, English), plus language-neutral artifacts.

Register the marketplace once, enable the plugin per project.

## Skill

| Skill | What it does |
|---|---|
| `anti-slop` | Names why a draft sounds generated, and replaces the slop with the concrete thing. Ships 1894 entries (1856 distinct) across four grep-checked lists plus a flexion-aware checker script. |

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
a severity, and `data/severity-overrides.json` demotes vocabulary that collides
with real code — `aria` matches every `aria-label`, and so do `transform`,
`manifest`, `key` and `harness`.

Measured on 17 500 words of technical documentation: **5.5** hard hits per 1000
words before the overrides, **0.5** after, with the genuine findings intact.

## The lists

| File | Terms |
|---|---|
| `slop-list.json` | 517 · upstream EQ-Bench, unmodified |
| `slop-list-en-extra.json` | 772 · curated English |
| `slop-list-de.json` | 496 · curated German |
| `slop-list-universal.json` | 109 · stock names and places, chatbot artifacts, placeholders |

No comparable public German list exists — `slop-list-de.json` was built for this
plugin. Third-party sources and their licences are credited in the repo `NOTICE`.

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
