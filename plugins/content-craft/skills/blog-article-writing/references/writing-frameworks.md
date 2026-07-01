# Writing Frameworks

Detailed guide to structural frameworks for blog articles, with full skeletons and usage notes.

---

## Table of Contents

1. [Problem → Struggle → Resolution](#problem--struggle--resolution)
2. [AIDA (Attention → Interest → Desire → Action)](#aida)
3. [PAS (Problem → Agitate → Solution)](#pas)
4. [Problem → Cause → Options → Recommendation](#problem--cause--options--recommendation)
5. [Case Study / Postmortem](#case-study--postmortem)
6. [FAQ / Myth-busting](#faq--myth-busting)
7. [BAB (Before → After → Bridge)](#bab)
8. [Choosing the Right Framework](#choosing-the-right-framework)

---

## Problem → Struggle → Resolution

**Best for:** Technical blogs, engineering posts, experience reports.

This is the most natural narrative arc and works for almost any topic. It maps roughly to a condensed Hero's Journey without the storytelling theater.

### Full Skeleton

```markdown
# [Headline: Outcome or Tension]

## The Problem
- Describe the concrete situation
- Why it's painful for the reader's specific role
- What's at stake if it's not solved

## What We Tried (and Why It Failed)
- Approach 1: what it was, why it seemed right, where it broke
- Approach 2: what it was, why it seemed right, where it broke
- Pattern: what the failures had in common

## What Actually Worked
- The solution / insight / approach
- Why it worked where others didn't
- Concrete implementation details (code, config, steps)

## Results
- Specific metrics, before/after
- Caveats and limitations
- What we'd do differently

## What This Means for You
- 2–3 actionable takeaways
- How to adapt this to the reader's situation
```

### Example Opening

> We needed to cut our ML inference costs without sacrificing latency. After three months of
> optimization dead-ends — batching, model distillation, spot instances — we found that the
> real bottleneck wasn't compute at all.

---

## AIDA

**Best for:** Opinion pieces, product launches, posts with a clear CTA.

Originally from advertising (1898, E. St. Elmo Lewis), AIDA guides the reader from noticing to acting. Adapt to blog voice — avoid sleazy sales copy.

### Full Skeleton

```markdown
# [Headline: Spark curiosity or state outcome]

## [Opening Hook — Attention]
- Surprising stat, bold claim, or relatable pain
- 2–3 sentences maximum

## [Context & Why It Matters — Interest]
- Expand on the hook with context
- Show the reader you understand their world
- Build the case for why this topic matters *now*

## [Show What's Possible — Desire]
- Concrete examples, case studies, before/after
- Paint the picture of the outcome
- Address objections ("but what about…")

## [What To Do Next — Action]
- Specific next step (not just "subscribe")
- Give a decision framework, a checklist, or a first action
- End with confidence, not desperation
```

### When NOT to Use AIDA

- Deep technical reference articles (too promotional in tone)
- Postmortems (the "Desire" phase feels forced)
- Anything where the reader already knows they need the information

### Critical Note

Over-using AIDA makes everything sound like a landing page. For blog articles, soften "Desire" into honest realistic upside and make "Action" genuinely useful rather than a sales pitch.

---

## PAS

**Best for:** Short-form content, email newsletters, social posts, problem-focused articles.

PAS (Problem → Agitate → Solution) works by making the reader *feel* the problem before presenting the fix.

### Full Skeleton

```markdown
# [Headline: Name the pain or tension]

## The Problem
- State the problem in the reader's own words
- Be specific about who has this problem and when

## Why It's Worse Than You Think (Agitate)
- Consequences of ignoring it
- Hidden costs, second-order effects
- "You've probably tried X, and it didn't work because…"

## Here's What Works (Solution)
- The approach, with concrete steps
- Why it addresses the root cause, not symptoms
- Evidence: numbers, examples, screenshots
```

### Softening Agitate for Blog Posts

In a blog (vs. ad copy), replace artificial urgency with honest tension:

| Sales Copy (avoid) | Blog Voice (prefer) |
|---------------------|---------------------|
| "You're losing $10K every day!" | "Teams we've seen ignore this tend to hit the same wall 3–6 months later." |
| "Don't be left behind!" | "Here's why the default approach breaks at scale." |
| "Act now before it's too late!" | "If this matches your situation, here's a starting point." |

---

## Problem → Cause → Options → Recommendation

**Best for:** Analytical or consulting-style posts where readers want "what should I do?"

### Full Skeleton

```markdown
# [Headline: Decision-oriented]

## The Problem
- Concrete description of the issue
- Who faces it and when

## Root Cause Analysis
- Why this happens (not just symptoms)
- Contributing factors
- Common misconceptions about the cause

## Options
### Option A: [Name]
- How it works
- Pros / Cons
- When it's the right choice

### Option B: [Name]
- How it works
- Pros / Cons
- When it's the right choice

### Option C: [Name]
- How it works
- Pros / Cons
- When it's the right choice

## Recommendation
- Which option and why (for the defined audience)
- Decision framework for different situations
- How to get started
```

---

## Case Study / Postmortem

**Best for:** Technical and business audiences. Very sticky — readers remember stories with specific details.

### Full Skeleton

```markdown
# [Headline: Specific story + outcome]

## Situation
- What was the context? (team size, stack, constraints)
- What triggered this work?

## Constraints
- Budget, timeline, team, technical limitations
- Non-negotiable requirements

## Options Considered
- Option 1: brief description + why it was on the table
- Option 2: brief description + why it was on the table
- Option 3: brief description + why it was on the table

## What We Chose (and Why)
- The decision
- The reasoning — what tipped the scales
- What we explicitly traded off

## Outcome
- Quantitative results (metrics, before/after)
- Qualitative results (team feedback, user response)
- Surprises — what we didn't expect

## Lessons Learned
- What we'd do the same
- What we'd do differently
- Advice for someone in a similar situation
```

---

## FAQ / Myth-busting

**Best for:** SEO, scannability, topics with common misconceptions.

### Full Skeleton

```markdown
# [Headline: "X Things You Think You Know About Y"]

## Introduction
- Why these misconceptions matter (1–2 paragraphs)

## Myth 1: "[Common belief]"
**Reality:** [Crisp correction with evidence]

## Myth 2: "[Common belief]"
**Reality:** [Crisp correction with evidence]

...repeat 5–10 times...

## What Actually Matters
- Synthesize the key truths
- Actionable summary
```

---

## BAB

**Best for:** Short-form social posts, promotional blurbs, quick newsletter sections.

BAB (Before → After → Bridge) is concise and works in tight spaces.

### Skeleton

```markdown
**Before:** [Describe the painful status quo]
**After:** [Paint the desirable outcome]
**Bridge:** [Show how to get from Before to After]
```

### Example

> **Before:** Your team spends 3 hours per deploy manually checking configs across 4 environments.
> **After:** Deploys take 12 minutes, configs are validated automatically, and drift is caught before it hits production.
> **Bridge:** Here's the Terraform module and CI pipeline we built to make that happen.

---

## Choosing the Right Framework

| Your goal | Use this |
|-----------|----------|
| Share a technical experience | Problem → Struggle → Resolution |
| Persuade toward a specific action | AIDA |
| Address a pain point directly | PAS |
| Compare options and recommend | Problem → Cause → Options → Rec |
| Tell a specific real-world story | Case Study / Postmortem |
| Address common questions/myths | FAQ / Myth-busting |
| Quick social or newsletter blurb | BAB |

**Remember:** Frameworks are code templates — useful, but you still need good logic and domain understanding. Treat them as scaffolding, not crutches.
