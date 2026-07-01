# Practice Drills

Pragmatic exercises to turn blog writing skills into habits.

---

## Table of Contents

1. [Headline Sprint](#headline-sprint)
2. [Readability Refactor](#readability-refactor)
3. [Narrative Rewrite](#narrative-rewrite)
4. [Brutal Edit with Targets](#brutal-edit-with-targets)
5. [Audience Flip](#audience-flip)
6. [Hook Gauntlet](#hook-gauntlet)

---

## Headline Sprint

**Goal:** Build the habit of exploring multiple framings before committing to one.

### The Drill

1. Pick a topic you're about to write about
2. Set a 10-minute timer
3. Write 15 headline variants using different patterns:
   - 3× Outcome + Constraint
   - 3× Tension / Counterintuitive
   - 3× Specific Story
   - 3× Direct Question
   - 3× How-To with Specificity
4. Circle the top 3
5. Ask: "Which would make a smart peer click if they saw it in their feed?"

### Example: Topic = "Reducing Docker Image Size"

1. "How to Cut Your Docker Images from 1.2GB to 47MB"
2. "Your Docker Images Are 10x Bigger Than They Need to Be"
3. "We Reduced Our Container Registry Costs by 80% with Multi-Stage Builds"
4. "Why Is Your Production Image Still Based on Ubuntu?"
5. "Small Docker Images, Fast Deploys: A Practical Guide for Go Services"
6. "The 3 Layers That Make Your Docker Image Huge (and How to Fix Each)"
7. "Docker Image Hygiene: What Your CI Pipeline Should Check"
8. "How We Debug Slim Docker Images Without SSH"
9. "Is Your Docker Image Smaller Than Your Node Modules?"
10. "Multi-Stage Builds Aren't Enough: What Else You Need for Slim Images"

### Ongoing Habit

Keep a **swipe file** — a running document of headlines that made *you* click. For each, note:
- The headline
- Where you saw it
- Why you clicked (tension? specificity? relevance?)
- What pattern it uses

---

## Readability Refactor

**Goal:** Build the muscle for simple writing without losing technical depth.

### The Drill

1. Take an old dense post, documentation page, or paper abstract
2. **Constraint:** Rewrite it so average sentence length ≤ 18 words
3. **Rule:** No technical content may be lost
4. Compare before/after for clarity

### Example

**Before** (avg 31 words/sentence):
> The implementation of the distributed caching layer, which was designed to reduce the latency of database queries that were frequently executed across multiple microservices in our production environment, resulted in a significant improvement in overall system performance as measured by p99 response times.

**After** (avg 12 words/sentence):
> We added a distributed cache between our microservices and the database. It targets the most frequent queries. P99 response times dropped by 40%. Here's how we set it up and what we'd change.

### Scoring

Count sentences and total words. Divide. If average > 20 words, keep cutting. If < 12, you might be over-fragmenting — vary the rhythm.

---

## Narrative Rewrite

**Goal:** Practice turning dry information into engaging stories.

### The Drill

1. Pick one dry how-to post or documentation page
2. Rewrite it into **Case Study** format:
   - Situation → Attempts → Failure modes → Final approach → Lessons
3. Keep the same technical content
4. Add: who was involved, what went wrong, what surprised you

### Example Transformation

**Before (How-To):**
> To set up Prometheus alerting, configure alert rules in prometheus.yml, set up Alertmanager
> with your notification channels, and create recording rules for expensive queries.

**After (Case Study):**
> Last quarter, our on-call engineer got paged 47 times in one week. 41 of those alerts were
> noise. We spent two sprints rebuilding our Prometheus alerting from scratch. Here's what we
> changed:
>
> **The problem:** Our alert rules were copy-pasted from a blog post written for a different
> architecture. They triggered on symptoms, not causes.
>
> **What we tried first:** Raising thresholds. This just meant we caught problems later.
>
> **What actually worked:** We rewrote alerts to target the 5 failure modes we'd actually
> seen in production. We added recording rules for the expensive queries that were slowing
> Prometheus itself. And we routed alerts through Alertmanager with severity-based channels.
>
> **Result:** Pages dropped from 47/week to 6. False positive rate went from 87% to 12%.

---

## Brutal Edit with Targets

**Goal:** Build the "kill your darlings" muscle.

### The Drill

1. Take a draft (yours or someone else's, with permission)
2. Note the word count
3. **Target:** Cut 25–30% of the words without losing information
4. Rules:
   - No information may be lost
   - No meaning may change
   - You *must* hit the target
5. Read the result aloud — it should sound tighter and more confident

### Cut Priority Order

1. **Throat-clearing intros** (paragraphs before you get to the point)
2. **Repeated points** (keep the stronger version)
3. **Filler phrases** ("in order to", "it should be noted")
4. **Decorative adjectives/adverbs** ("incredibly", "absolutely", "very")
5. **Obvious statements** (things your audience already knows)
6. **Meta-commentary** ("as mentioned earlier", "in this section we'll discuss")

### Scoring

| Reduction | Rating |
|-----------|--------|
| 30%+ | Excellent — the draft was bloated but you've got sharp editing instincts |
| 20–30% | Good — typical range for a solid edit |
| 10–20% | The draft was already decent, or you need to be more ruthless |
| < 10% | Either exceptional first draft or you're not cutting hard enough |

---

## Audience Flip

**Goal:** Practice writing the same content for different audiences.

### The Drill

1. Pick a technical topic you know well
2. Write a 200-word summary for:
   - **Audience A:** A senior engineer on your team
   - **Audience B:** A non-technical product manager
   - **Audience C:** A CTO evaluating a technology decision
3. Compare: what changed? What stayed?

### What to Notice

- The *facts* stay the same; the *framing* changes
- Technical depth increases for engineers, business impact increases for PMs/CTOs
- Jargon is fine for peers, must be translated for others
- The "so what?" is different for each audience

---

## Hook Gauntlet

**Goal:** Practice writing opening hooks for maximum impact.

### The Drill

1. Pick a topic
2. Write 5 different opening hooks (3–4 sentences each), using different formulas:
   - **Situation → Surprise → Promise**
   - **Bold Claim → Qualification → Road Map**
   - **Relatable Pain → "Here's Why" → Preview**
   - **Specific Number → Context → Stakes**
   - **Question → Tension → "Let me show you"**
3. Rank them: which one would make your target reader keep going?

### Selection Criteria

- Does it name the reader or their situation?
- Does it create tension or curiosity?
- Does it promise something concrete?
- Is it honest? (Would the article actually deliver on this promise?)
- Would *you* keep reading?
