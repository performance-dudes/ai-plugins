# anti-slop — plugin state

Current-state documentation for the `anti-slop` plugin (intent lives in
`specs/anti-slop/0001_product_anti-slop.md`; the running log is in `journal/`).

## What it is

A prose-editing plugin that finds LLM slop in German and English, in business and
narrative registers. It ships one skill, three term lists, a severity-override
file and a checker script. The lists are **data**, never loaded into context —
they are queried by script.

## Components

| Component | Purpose |
|---|---|
| `skills/anti-slop/SKILL.md` | Entry point and index: the one rule, hard/soft, the cross-register bans, how to run the checker. |
| `references/business-prose.md` | English business register — openers, verb inflation, hype adjectives, connective padding. |
| `references/narrative-prose.md` | English fiction — dialogue attribution, adverbs, body-language clichés, chapter cadences, stock names. |
| `references/german-prose.md` | German, both registers, plus the five patterns no word list can catch. |
| `scripts/check-slop.py` | The checker: flexion-aware matching, language detection, density reporting. |
| `data/slop-list*.json` | The three term lists. |
| `data/severity-overrides.json` | 71 terms demoted to soft: technical vocabulary, ordinary English, and register markers of literary or academic prose. |

## How the checker decides

1. **Language** is detected from function-word frequency unless `--lang` is given.
2. **Lists load universal-first**, then the language list. The first severity for
   a term wins — that is what keeps a stock name soft when a language list would
   rank the same term hard. For this to have any effect, the universal list must
   actually carry those names; a name that sits only in a language list is beyond
   the rule's reach.
3. **Each term becomes a regex.** A trailing `*` allows up to five suffix
   characters (German inflection). Terms that start or end with punctuation use
   a lookaround instead of `\b`, so `Selbstverständlich!` still matches.
4. **Overrides apply per term as it is loaded**, demoting listed terms to soft
   before the first-severity-wins rule takes effect.
5. **Output** groups hits by category and severity and reports hits per 1000
   words.

## Design decisions worth knowing

**Stock names are always soft — invented places are not.** `Chen`, `Reed`, `Kai`
and `Mara` are real people's names, so a hit there means "check whether this name
was chosen or generated", never "rename this person". `Eldoria`, `Whisperwood`
and `Zephyria` belong to nobody and stay hard under `stock-place`. The split
exists because it was briefly missing: names and places were moved into the
universal list together, the places went soft with them, and a sample of
generated English fiction dropped from 211 hard hits per 1000 words to zero. The
eval case `g05-narrative-en` now covers exactly that gap.

**Formatting tells are not in the lists.** Uniform paragraph length,
header-per-paragraph, bolded-term bullets and emoji scaffolding are descriptions,
not searchable strings. They live in the prose references, where a human reads
them.

**The prose outranks the data.** The lists store word forms rather than lemmas,
so a gap is always possible — `seamlessly` can sit on a list while `seamless`
does not, although the skill bans both. The category tables in the SKILL.md are
therefore authoritative, and a miss in a data file is not an acquittal.

**Dead entries are a test failure.** Entries like `cultivating/fostering` or
`boasts/features/maintains/offers [a]` read like terms but can never match as a
literal. `tests/anti-slop/run.sh` rejects them (AC-4-3); 32 were removed before
the first release.

## Known limits

- The terms are curated, not measured. No frequency corpus backs the lists, so
  severity is an editorial judgement rather than a statistic — which is why every
  hard hit is still a question, not a verdict.
- Language detection is a function-word heuristic. A German draft quoting long
  English passages may be scored with the wrong list — pass `--lang both`.
- The checker reads plain text. It does not skip code blocks, so a Markdown file
  full of code may report artifacts from the code rather than the prose.
