---
name: anti-slop
description: Detects and removes LLM slop — the words, phrases and cadences statistically over-represented in generated text, which make prose read as machine-written. Ships 1843 entries across three lists (English, German, and language-neutral chatbot artifacts, stock names and unfilled placeholders) plus a flexion-aware checker, covering business prose (email, offer, LinkedIn, blog, column) and narrative prose (fiction, chapters, dialogue) in both languages. Use when drafting, editing or reviewing any prose a human will read; when a draft "sounds like AI" and the reason must be named; when building a ban list, style guide or automated prose check. Trigger terms — slop, GPT-ism, AI-sounding, sounds like ChatGPT, purple prose, generic phrasing, delve, tapestry, testament to, "barely above a whisper", em-dash tell, prose polish, style ban list, does this read as written by AI; KI-Floskeln, KI-Fluff, klingt nach ChatGPT, Floskeln streichen, Textglättung, Lektorat, liest sich wie KI, deutsche Slop-Liste.
---

# Anti-Slop — removing the machine tell from prose

Three lists under `${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/data/`. Never load one
into context — check with the script below.

| File | Entries | Scope |
|---|---|---|
| `slop-list-en-extra.json` | 1190 | English business and narrative prose |
| `slop-list-de.json` | 496 | German business and narrative prose |
| `slop-list-universal.json` | 157 | language-neutral: stock names (soft) and places (hard), chatbot artifacts, unfilled placeholders |

Every list is curated and extended here; each entry carries a category and a
hard/soft severity. The universal list is loaded on **every** run: `Elara`,
`oaicite`, `[Company Name]` and `utm_source=chatgpt.com` do not care what
language the draft is in. `slop-list-de.json` was built for this skill.

## The one rule

**Replace the slop with the concrete thing.** Slop is almost always a placeholder
where a specific noun, number or action belongs.

| Slop | Fix |
|---|---|
| "harness AI's transformative potential" | "three engineers, six weeks, fixed price" |
| „zahlreiche Kunden profitieren" | „elf Kunden, davon vier seit 2024" |
| "she said, her voice barely above a whisper" | "she said. The room did not move." |

Deleting without replacing is allowed when no information is lost.

## Register and language decide which reference applies

| Register | Read |
|---|---|
| **Business / non-fiction, English** | [references/business-prose.md](references/business-prose.md) |
| **Narrative / fiction, English** | [references/narrative-prose.md](references/narrative-prose.md) |
| **Any register, German** | [references/german-prose.md](references/german-prose.md) |

German is not translated English slop. It inflects, its tells come from
administrative and business German rather than from the model alone, and half
its terms are ordinary words that only convict in clusters. Read
`german-prose.md` before editing German prose.

## Hard versus soft

Every term carries a severity.

| | Meaning | Action |
|---|---|---|
| **hard** | a tell in isolation — `bahnbrechend`, `delve`, `Zusammenfassend lässt sich sagen` | cut, unless quotation or technical term |
| **soft** | legitimate on its own — `zudem`, `umfassend`, `nicht nur … sondern auch` | a finding only in a cluster; one hit proves nothing |

`data/severity-overrides.json` demotes terms to soft regardless of which list
they sit in, in three classes:

1. **Technical vocabulary that collides with real code** — `aria` matches every
   `aria-label`, plus `transform`, `manifest`, `key`, `harness`.
2. **Ordinary language too common to convict alone** — `rich`, `such as`,
   `overall` · `entscheidend*`, `unzählig*`.
3. **Register markers** — vocabulary that marks literary or academic prose rather
   than machine prose: `profound`, `charming`, `anchor`, `convey` · `mannigfaltig*`,
   `in der tat`, `äußerst`, `ohne zweifel`.

**Stock names are always soft, on purpose.** `Chen`, `Reed`, `Kai` and `Mara` are
real people's names. A name hit means *check whether this name was chosen or
generated* — in a licensed universe, against the source material — never
"rename this person".

**Places are not.** Invented ones (`Eldoria`, `Whisperwood`, `Zephyria`) belong to
nobody, and the real towns on the list (`Maplewood`, `Seabrook`, `Ravenswood`) are
the ones models reach for by default — both stay hard under `stock-place`. **Never
move a place to `stock-name` to silence it** — places are the sharpest signal the
lists carry for generated fiction.

## The tells that cross both registers

Cut these from any draft you write, unless they are quotation or carry a technical
meaning (see "What is *not* slop"). This table is an editing rule and outranks the
data files: the checker ranks some of these soft because they also occur in human
prose, but in your own draft they are still placeholders.

| Category | Never |
|---|---|
| Metaphor shells | tapestry, symphony, kaleidoscope, labyrinth, a testament to · Sinfonie, Kaleidoskop, ein Tanz aus, die Spitze des Eisbergs |
| Journey framing | delve, dive into, embark, navigate, journey, realm · eintauchen, Reise, Landschaft, die Welt der |
| Hype adjectives | seamless, cutting-edge, transformative, game changer · nahtlos, bahnbrechend, revolutionär, wegweisend, Gamechanger |
| Filler intensifiers | meticulous, intricate, crucial, countless · akribisch, zahlreich |
| Summary tells | in conclusion, it's important to note · Zusammenfassend lässt sich sagen, Es ist wichtig zu beachten, Letzten Endes |
| Chatbot residue | as an AI language model, I hope this helps, You're absolutely right! · Selbstverständlich!, Als KI-Sprachmodell |
| Letter formulas | I hope this email finds you well, at your earliest convenience · Ich hoffe, es geht Ihnen gut, Zögern Sie nicht |

## How to check a draft

```bash
${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/scripts/check-slop.py draft.md              # language auto-detected
${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/scripts/check-slop.py --lang both draft.md  # mixed-language draft
${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/scripts/check-slop.py --hard-only draft.md  # skip terms legitimate in isolation
${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/scripts/check-slop.py --context draft.md    # show the line each hit sits on
```

Output groups hits by category and severity and reports **hits per 1000 words** —
that density, not any single hit, is what decides whether soft terms convict.
Human prose sits near zero hard hits per 1000 words; generated drafts land two to
three orders of magnitude higher. Overlapping entries count once: "is a testament
to" is one hit, not four. Exit code 0 = no hit, 1 = at least one hit (soft
included), 2 = the draft could not be read.

**Why a script and not a grep.** German inflects: a `\b`-anchored search for
`entscheidend` misses `entscheidende`, `entscheidender`, `entscheidendes`, which
is how the word actually occurs. Entries ending in `*` match the stem plus a
short suffix. A plain grep finds roughly none of them.

To check one phrase by hand:

```bash
grep -i 'nahtlos' "${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/data/slop-list-de.json"
```

### Data-file gotchas

- All three lists share one shape, `[term, category, severity]`. A loader branch
  for any other shape is a bug, not a feature: a term without a severity column
  gets treated as hard and escapes the universal-list rule.
- **The lists hold word forms, not lemmas, and have gaps because of it:** a list
  can carry an adverb (`collaboratively`) without its adjective (`collaborative`).
  The category table in "The tells that cross both registers" outranks the data
  files — a term missing from a list is not an acquittal.
- Entries are stored lowercase and matched case-insensitively; a term is
  `strip()`ed on load, so surrounding whitespace never belongs to the term.
- **An entry must be as specific as the tell.** `i cannot` is ordinary English
  and matched 83 times in one Austen novel; the tell is `i cannot fulfill`. When
  a term is ordinary language plus a marked continuation, the continuation
  belongs in the entry.
- **Ordinary language that marks a register goes in `severity-overrides.json`,
  not out of the list.** `profound` and `mannigfaltig*` stay on the lists and
  still count toward density — they just stop convicting alone.
- `slop-list-de.json` is not in alphabetical order (the two English lists are) —
  grep it, do not eyeball it.
- Formatting tells (uniform paragraph length, header-per-paragraph, bolded-term
  bullets, emoji scaffolding) are deliberately **not** in the lists: they are
  descriptions, not searchable strings. They live in the prose references.

## What is *not* slop

1. **Technical meaning.** "harness" for a test harness, `gemäß` in a contract,
   "navigate" for actual navigation. The lists ban the metaphor, not the word.
2. **Quotation.** Never edit slop out of someone else's quoted words.
3. **A word that carries the sentence.** If removing it loses information, it
   was not a placeholder. Slop is what can be deleted without loss.
4. **A lone soft hit.** German soft terms are ordinary German. One `zudem` is a
   word; five in two paragraphs is a finding.
5. **A real person's name.** A `stock-name` hit asks whether the name was chosen
   or generated — never rename a real person over it.

Do not run any list as find-and-replace. Every hit is a question, not a verdict.

## Anti-pattern: over-correction

No thesaurus replacements. The fix for "a tapestry of challenges" is "four
blockers", never "a variegated arras of tribulations". The German trap is the
same in reverse: replacing `nutzen` with `verwenden` changes nothing — the
sentence needed a number, not a synonym.

**The em-dash caveat.** The em-dash is widely called an AI tell and is *not* on
any list here. Treat it as a house-style question, not a slop question — some
style guides ban it, this skill does not.
