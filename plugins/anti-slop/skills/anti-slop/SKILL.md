---
name: anti-slop
description: Detects and removes LLM slop — the words, phrases and cadences statistically over-represented in generated text, which make prose read as machine-written regardless of intent. Ships 1894 entries (1856 distinct terms) across four lists (English, German, and language-neutral chatbot artifacts, stock names and unfilled placeholders) plus a flexion-aware checker, covering business prose (email, offer, LinkedIn, blog, column) and narrative prose (fiction, chapters, dialogue) in both languages. Use when drafting, editing or reviewing any prose a human will read; when a draft "sounds like AI" and the reason must be named; when building a ban list, style guide or automated prose check. Trigger terms — slop, GPT-ism, AI-sounding, sounds like ChatGPT, purple prose, generic phrasing, delve, tapestry, testament to, "barely above a whisper", em-dash tell, prose polish, style ban list, does this read as written by AI; KI-Floskeln, KI-Fluff, klingt nach ChatGPT, Floskeln streichen, Textglättung, Lektorat, liest sich wie KI, deutsche Slop-Liste.
---

# Anti-Slop — removing the machine tell from prose

Four lists under `${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/data/`. Never load one
into context — check with the script below.

| File | Terms | Source |
|---|---|---|
| `slop-list.json` | 517 | [sam-paech/antislop-sampler](https://github.com/sam-paech/antislop-sampler), EQ-Bench Slop Score |
| `slop-list-en-extra.json` | 772 | [Corpus of AI Cliches](https://github.com/AIStoryHub/AIStoryHub_LLM_Cliche_Corpus) (MIT) · [SLOP_Detector](https://github.com/SicariusSicariiStuff/SLOP_Detector) (Apache-2.0) · [document-lens](https://github.com/michael-borck/document-lens-legacy) (MIT) · en.wikipedia *Signs of AI writing* (CC BY-SA) |
| `slop-list-de.json` | 496 | curated here — de.wikipedia *Anzeichen für KI-generierte Inhalte* (CC BY-SA), German editorial practice |
| `slop-list-universal.json` | 109 | language-neutral: stock names (soft) and places (hard), chatbot artifacts, unfilled placeholders — from the same MIT/Apache sources as the row above |

The universal list is loaded on **every** run: `Elara`, `oaicite`,
`[Company Name]` and `utm_source=chatgpt.com` do not care what language the draft
is in. No comparable public German list exists — `slop-list-de.json` was built
for this skill.

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

The curated lists carry a severity per term; the upstream EQ-Bench list does not
(treat every one of its hits as hard).

| | Meaning | Action |
|---|---|---|
| **hard** | a tell in isolation — `bahnbrechend`, `delve`, `Zusammenfassend lässt sich sagen` | cut, unless quotation or technical term |
| **soft** | legitimate on its own — `zudem`, `umfassend`, `nicht nur … sondern auch` | a finding only in a cluster; one hit proves nothing |

`data/severity-overrides.json` demotes a small set of terms to soft regardless
of which list they came from: technical vocabulary that collides with real code
(`aria` matches every `aria-label`, plus `transform`, `manifest`, `key`,
`harness`) and ordinary English too common to convict alone (`rich`, `such as`,
`overall`). Without it, 17 500 words of technical documentation produced 5.5 hard
hits per 1000 words; with it, 0.5 — the same rate as hand-written prose, with the
real findings intact.

**Stock names are always soft, on purpose.** `Chen`, `Reed`, `Kai` and `Mara` are
real people's names. A name hit means *check whether this name was chosen or
generated* — in a licensed universe, against the source material — never
"rename this person".

**Invented places are not.** `Eldoria`, `Whisperwood` and `Zephyria` belong to
nobody, so they stay hard under their own category `stock-place`. They are among
the sharpest signals the lists carry; demoting them along with the people cost
an English fiction sample its entire hard score before this split existed.

## The tells that cross both registers

Ban unconditionally.

| Category | Never |
|---|---|
| Metaphor shells | tapestry, symphony, kaleidoscope, labyrinth, a testament to · Sinfonie, Kaleidoskop, ein Tanz aus, die Spitze des Eisbergs |
| Journey framing | delve, dive into, embark, navigate, journey, realm · eintauchen, Reise, Landschaft, die Welt der |
| Hype adjectives | seamless, cutting-edge, transformative, game changer · nahtlos, bahnbrechend, revolutionär, wegweisend, Gamechanger |
| Filler intensifiers | meticulous, intricate, crucial, countless · akribisch, entscheidend, zahlreich, unzählig, äußerst |
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
Calibration: hand-written reference texts measured 0–0.5 hard hits per 1000
words; generated drafts run two to three orders of magnitude above that. The eval
draws its pass line higher, at 1.0, so normal variation in human prose does not
fail a case — the measured range is where texts land, the threshold is what is
still allowed.

**Why a script and not a grep.** German inflects: a `\b`-anchored search for
`entscheidend` misses `entscheidende`, `entscheidender`, `entscheidendes`, which
is how the word actually occurs. Entries ending in `*` match the stem plus a
short suffix. A plain grep finds roughly none of them.

To check one phrase by hand:

```bash
grep -i 'nahtlos' "${CLAUDE_PLUGIN_ROOT}/skills/anti-slop/data/slop-list-de.json"
```

### Data-file gotchas

- The upstream English JSON is `[term, probability_adjustment]`; lower adjustment
  means more heavily over-represented. The three curated files are
  `[term, category, severity]`.
- **The upstream list holds word forms, not lemmas, and has gaps because of it:**
  it carries `seamlessly` but not `seamless`, though this skill bans both. The
  category tables above outrank the data files — a miss is not an acquittal.
- Upstream entries are stored with a leading comma (`, once a`). They are
  `strip()`ed on load, so they match as `once a` — the comma is storage, not part
  of the term. (An older note claimed they collapse to `""` and are skipped; they
  do not, and none of the 517 entries does.)
- Term order is not alphabetical — grep, do not eyeball.
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
5. **A real person's name.** See the stock-name note above.

Do not run any list as find-and-replace. Every hit is a question, not a verdict.

## Anti-pattern: over-correction

No thesaurus replacements. The fix for "a tapestry of challenges" is "four
blockers", never "a variegated arras of tribulations". The German trap is the
same in reverse: replacing `nutzen` with `verwenden` changes nothing — the
sentence needed a number, not a synonym.

**The em-dash caveat.** The em-dash is widely called an AI tell and is *not* on
any list here. Treat it as a house-style question, not a slop question — some
style guides ban it, this skill does not.
