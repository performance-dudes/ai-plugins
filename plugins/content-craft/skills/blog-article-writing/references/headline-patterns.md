# Headline Patterns

A pattern library for crafting headlines and hooks that earn attention without resorting to clickbait.

---

## Table of Contents

1. [Why Headlines Matter](#why-headlines-matter)
2. [Pattern Library](#pattern-library)
3. [Opening Hook Formulas](#opening-hook-formulas)
4. [Anti-Patterns](#anti-patterns)
5. [Headline Sprint Drill](#headline-sprint-drill)

---

## Why Headlines Matter

The headline and first few lines dominate whether people start reading. Research across thousands of field experiments (Washington Post, Upworthy) shows that simpler, more readable headlines get significantly more clicks and deeper processing.

More information density early on correlates with longer reading times. The headline is activation energy — it must get the reader over "why bother" into the basin where they'll gladly roll through the rest.

---

## Pattern Library

### Pattern 1: Outcome + Constraint

Frame the result *and* the limitation that makes it realistic.

| Example | Why it works |
|---------|-------------|
| "How to Ship Reliable ML Models with a Team of 3" | Specificity signals real experience |
| "Building a Search Engine on a $200/month Budget" | Constraint creates tension and relevance |
| "Zero-Downtime Migrations Without a DBA" | Reader self-selects: "that's my situation" |

### Pattern 2: Tension / Counterintuitive

Challenge an assumption or reveal a hidden cost.

| Example | Why it works |
|---------|-------------|
| "The Hidden Cost of 'Just Use a Vector DB'" | Challenges a popular lazy default |
| "Why Your Best Engineers Should Write the Docs" | Counterintuitive → curiosity gap |
| "Stop Optimizing for Latency (Optimize for This Instead)" | Challenges conventional wisdom |

### Pattern 3: Specific Story

Lead with a concrete, quantified result from real experience.

| Example | Why it works |
|---------|-------------|
| "We Cut Our Inference Bill by 63%: What Actually Worked" | Specific number = credibility |
| "How a 3-Line Config Change Fixed Our Deployment Pipeline" | Simplicity of fix creates curiosity |
| "The Outage That Taught Us to Stop Trusting Our Dashboards" | Story + lesson = compelling |

### Pattern 4: Direct Question

Ask something the target reader is already wondering.

| Example | Why it works |
|---------|-------------|
| "Is Your CI Pipeline Lying to You?" | Reader instantly self-checks |
| "What Happens When Your LLM Provider Goes Down?" | Names a fear they haven't planned for |
| "Should You Build or Buy Your Observability Stack?" | Frames a real decision |

### Pattern 5: How-To with Specificity

Classic but only works when specific enough to signal real depth.

| Example | Why it works |
|---------|-------------|
| "How to Debug Memory Leaks in Go Microservices" | Specific stack + specific problem |
| "How We Migrated 2TB of Postgres Data with Zero Downtime" | Real scale, real constraint |

**Avoid:** "How to Improve Your Code" (too vague, no signal of depth).

### Pattern 6: List with a Twist

Numbers work — but only when the items are non-obvious or the framing is surprising.

| Example | Why it works |
|---------|-------------|
| "5 Prometheus Alerts That Actually Prevent Outages" | "Actually" signals non-obvious picks |
| "3 Architecture Decisions We Regret (and 2 We Don't)" | Honesty + specificity |

**Avoid:** "10 Tips for Better Code" (generic, no signal).

---

## Opening Hook Formulas

The first 3–4 sentences must:
1. **Name the reader and their situation**
2. **Name the tension or surprising angle**
3. **Promise a concrete payoff**

### Formula 1: Situation → Surprise → Promise

> "If you're running Kubernetes in production with fewer than 5 engineers, you've probably
> accepted that some things just break on Friday afternoons. But the pattern behind those
> failures is almost always the same — and once you see it, the fix is straightforward."

### Formula 2: Bold Claim → Qualification → Road Map

> "Most teams over-invest in monitoring and under-invest in alerting. That's not a hot take;
> it's a pattern we've seen across 40+ production environments. Here's how to tell if you're
> one of them, and what to do about it."

### Formula 3: Relatable Pain → "Here's Why" → Preview

> "You've refactored the code, updated the tests, and the PR got two approvals. Then the
> deploy fails anyway. The problem isn't your process — it's your environment parity. Here's
> how we fixed it."

### Formula 4: Specific Number → Context → Stakes

> "Our p99 latency jumped from 120ms to 3.4 seconds overnight. No code changes, no traffic
> spike. This post is the debugging story and the one-line fix we wish we'd found sooner."

---

## Anti-Patterns

Headlines and hooks to avoid:

| Anti-Pattern | Why it fails | Fix |
|-------------|-------------|-----|
| "Introduction to X" | No tension, no promise | "What X Gets Wrong (and How to Fix It)" |
| "A Deep Dive into Y" | Vague, overused | "How Y Works Under the Hood: [Specific Aspect]" |
| "Everything You Need to Know About Z" | Unrealistic scope, clickbait feel | "The 3 Things About Z That Actually Matter for [Role]" |
| "X is Dead" / "X is the Future" | Hyperbolic, rarely honest | "When X Makes Sense (and When It Doesn't)" |
| Generic "How to Improve" | No specificity signal | Add constraint, outcome, or audience |
| Misleading clickbait | Destroys trust | Match headline promise to actual content |
| Pun-based headlines | Clever ≠ clear; often confusing | Clarity over cleverness |

---

## Headline Sprint Drill

For each article, generate 10–15 headline variants using different patterns:

1. Write 3 Outcome + Constraint variants
2. Write 3 Tension / Counterintuitive variants
3. Write 2 Specific Story variants
4. Write 2 Direct Question variants
5. Write 2 How-To with Specificity variants

**Selection criteria:**
- Which one would make *you* click if a peer shared it?
- Which one most accurately represents the content?
- Which one works for the target reader's level of expertise?

**Swipe file habit:** Keep a running list of headlines that made you click. Reverse-engineer why: was it tension, specificity, a question, or social proof?
