# Editing Checklist

A structured three-pass editing method for turning drafts into sharp, readable articles.

---

## Table of Contents

1. [Why Separate Passes](#why-separate-passes)
2. [Pass 1: Structure](#pass-1-structure)
3. [Pass 2: Clarity](#pass-2-clarity)
4. [Pass 3: Brutal Cut](#pass-3-brutal-cut)
5. [Common Bloat Patterns](#common-bloat-patterns)
6. [Engagement vs. Depth Trade-off](#engagement-vs-depth-trade-off)

---

## Why Separate Passes

Readability and simplicity — strongly linked to engagement — are achieved mostly *in editing*, not drafting. Trying to fix structure, clarity, and wordiness simultaneously leads to overwhelm and missed problems.

**Rule of thumb:** Target 20–30% word reduction from first draft without losing information.

---

## Pass 1: Structure

Focus: Does the overall arc serve the defined reader and goal?

### Checklist

- [ ] **Audience & Intent visible?** Can you find the Who / Problem / Change at the top of the draft?
- [ ] **Does every section serve the defined reader?** If a section is "interesting to me but not to them," cut or move it
- [ ] **Is the framework clear?** Can a reader see the arc (Problem → Struggle → Resolution, AIDA, etc.)?
- [ ] **Does the opening hook earn attention?** Does it answer "why should I care now?" in the first 3–4 sentences?
- [ ] **Is the ending actionable?** Does the reader know what to *do* after reading?
- [ ] **Are subheadings descriptive?** Replace "Challenges" with "Why Naive Caching Breaks at Scale"
- [ ] **Is there a logical flow?** Does each section lead naturally to the next?
- [ ] **Is the scope right?** Too broad = shallow. Too narrow = not worth a post. Find the sweet spot.

### Red Flags

| Red Flag | Fix |
|----------|-----|
| Post tries to cover 5+ topics | Split into a series or pick the most valuable one |
| No clear "so what?" | Add explicit takeaways at the end of each major section |
| Buried lede | Move the key insight to the opening |
| Abrupt ending | Add a "What this means for you" section |

---

## Pass 2: Clarity

Focus: Are there paragraphs where a smart but tired reader would have to re-read?

### Checklist

- [ ] **One idea per sentence?** Split compound sentences that pack two ideas
- [ ] **One idea cluster per paragraph?** Break paragraphs longer than 4 sentences
- [ ] **Active voice?** Convert passive ("it was decided") to active ("the team decided")
- [ ] **Concrete verbs?** Replace "implement", "utilize", "facilitate" with "build", "use", "enable"
- [ ] **Defined jargon?** Any term a smart non-specialist might not know should be defined on first use
- [ ] **Consistent terminology?** Don't switch between "deploy", "release", "ship" for the same concept without reason
- [ ] **Are transitions smooth?** Each paragraph should connect to the previous one
- [ ] **Are examples concrete?** Replace "for example, a system" with "for example, our Postgres cluster on RDS"

### Quick Tests

1. **The "tired reader" test:** Read each paragraph imagining you're exhausted at 11 PM. Would you re-read any? Fix those.
2. **The "so what?" test:** After each paragraph, ask "So what?" If you can't answer in one sentence, the paragraph needs work.
3. **The "friend test":** Would you say this sentence to a colleague at a whiteboard? If not, rewrite it.

---

## Pass 3: Brutal Cut

Focus: Remove everything that doesn't earn its space.

### Cut Targets

| Target | Action |
|--------|--------|
| **Intro fluff** | First 1–3 paragraphs of a draft are often throat-clearing. Cut or compress to 1–2 sentences. |
| **Repetition** | If you make the same point twice, keep the stronger version |
| **Decorative adjectives** | "incredibly powerful framework" → "framework" |
| **Decorative adverbs** | "absolutely essential" → "essential"; "really important" → "important" |
| **Hedge words** | "somewhat", "fairly", "rather", "quite" — either commit or cut |
| **Meta-commentary** | "As I mentioned earlier…", "It's worth noting that…" — just state the thing |
| **Filler phrases** | See [Readability Guide](readability-guide.md) for the full list |
| **Obvious statements** | "Testing is important" — if your audience knows this, cut it |
| **Excessive qualifiers** | "In most cases, generally speaking, it tends to…" → "Usually, it…" |

### The 25% Challenge

1. Note your current word count
2. Calculate 75% of that number
3. Cut until you hit it
4. Read the result — it's almost always better

If you can't cut 25%, you probably can cut 15%. The exercise builds the "kill your darlings" muscle.

### What NOT to Cut

- Concrete examples and data points (these earn their space)
- Technical details that distinguish your post from surface-level content
- Necessary context for the target reader (but not for experts who already know)
- Transitions that maintain narrative flow

---

## Common Bloat Patterns

### Pattern 1: The Warm-Up Paragraph

**Before:**
> In today's fast-paced world of software development, teams are constantly looking for ways
> to improve their workflows. One area that often gets overlooked is the deployment pipeline.
> In this article, we'll explore how we improved our deployment pipeline and the lessons we learned.

**After:**
> Our deployment pipeline was burning 45 minutes per deploy. Here's how we cut it to 6.

### Pattern 2: The Hedging Stack

**Before:**
> It's perhaps worth considering that in many cases, it might be somewhat beneficial to
> potentially look into using structured logging in your application, as it could arguably
> help with debugging in certain situations.

**After:**
> Use structured logging. It cuts debugging time significantly — here's how.

### Pattern 3: The Restated Conclusion

**Before:**
> In conclusion, as we've seen throughout this article, structured logging is important for
> debugging. To summarize the key points we've discussed, structured logging helps with
> debugging, saves time, and improves observability. As mentioned earlier in this post,
> these benefits make structured logging a worthwhile investment.

**After:**
> **Key takeaway:** Add structured logging to your services. Start with request ID, duration,
> and error fields. Here's the config for your stack: [link].

### Pattern 4: The Unnecessary Definition

**Before:**
> Kubernetes, which is an open-source container orchestration platform originally developed
> by Google and now maintained by the CNCF, allows you to deploy and manage containerized
> applications at scale.

**After (for a DevOps audience):**
> (Don't define Kubernetes for a DevOps audience. They know.)

**After (for a general tech audience):**
> Kubernetes manages your containers across multiple servers — scaling, healing, and routing
> traffic automatically.

---

## Engagement vs. Depth Trade-off

Decide consciously where you sit on the spectrum:

| Dimension | Viral Snack | Deep Reference |
|-----------|-------------|----------------|
| **Length** | 800–1,200 words | 2,500–5,000+ words |
| **Tone** | Punchy, opinionated | Thorough, measured |
| **Structure** | AIDA, PAS, BAB | Case Study, Problem→Cause→Options |
| **Optimize for** | Shares, clicks, comments | Bookmarks, backlinks, return visits |
| **Engagement** | Higher short-term | Lower superficial, higher long-term |
| **Retention** | Often forgotten quickly | Referenced repeatedly |

### Guidelines

- For **"big idea" or reference pieces:** Accept lower superficial engagement; optimize for clarity and enduring value
- For **top-of-funnel or awareness posts:** Lean on hooks, story, and simplicity — as long as content remains honest
- **Don't pretend** a snack is a deep reference or vice versa. Set expectations in the headline.

Research shows design choices that boost on-page engagement can reduce information retention. Hyper-optimized clicky posts may get traffic but be forgotten; dense reference posts may get fewer views but stronger long-term impact.
