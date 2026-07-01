# Readability Guide

Research-backed principles for making text effortless to process without sacrificing depth.

---

## Table of Contents

1. [Research Findings](#research-findings)
2. [Core Readability Principles](#core-readability-principles)
3. [Filler Phrases to Cut](#filler-phrases-to-cut)
4. [Verb Upgrades](#verb-upgrades)
5. [Scannability Design](#scannability-design)
6. [Before/After Rewrites](#beforeafter-rewrites)
7. [The Complexity Paradox](#the-complexity-paradox)

---

## Research Findings

These are not opinions — they come from large-scale studies:

### Processing Fluency Effect
Social media users tend to enjoy content that is easily processed with high-frequency words and short sentence structures. This "fluency effect" holds up even when accompanied by information-rich content and processed in noisy contexts like reviewing a social media feed.

*Source: ASU Center for Services Leadership, based on Wiley Online Library research*

### Simpler Headlines Win
Thousands of field experiments across traditional (The Washington Post) and nontraditional news sites (Upworthy) showed that news readers are more likely to click on and engage with simple headlines than complex ones. Readers also better recognized phrases from simpler headlines.

*Source: Oppenheimer et al., PMC/NIH — "Reading Dies in Complexity"*

### Text Characteristics Drive Engagement
Posts with text that is easy to read, longer than 31 words (or 321 characters), and containing relevant hashtags tend to achieve higher engagement and awareness metrics.

*Source: International Journal of Information Management Data Insights, ScienceDirect*

### Engagement vs. Retention Trade-off
Design choices that boost on-page engagement (like inline annotations) can reduce information retention. Conversational prompts boosted engagement without reducing retention.

*Source: McInnis et al., CSCW 2022*

**Key insight:** The simplicity-engagement link is robust across contexts. In crowded information environments, people use writing simplicity as a heuristic for what they'll engage with.

---

## Core Readability Principles

### Sentence Level
- **One main idea per sentence**
- **Target ≤ 18 words average** sentence length
- **Vary rhythm:** mix short punchy sentences with occasional longer ones
- **Front-load the important word** in each sentence

### Paragraph Level
- **One idea cluster per paragraph**
- **2–4 sentences max** for web content
- **First sentence carries the point** — rest supports it
- **White space is a feature**, not waste

### Word Level
- **Prefer high-frequency words** (common, everyday vocabulary)
- **Use concrete nouns and verbs** over abstract ones
- **One-syllable words** when they work as well as multi-syllable alternatives
- **Define jargon once**, then use it freely

---

## Filler Phrases to Cut

These add words without adding meaning. Delete or replace on sight:

| Filler | Replacement |
|--------|-------------|
| "in order to" | "to" |
| "due to the fact that" | "because" |
| "at this point in time" | "now" |
| "in the event that" | "if" |
| "it is important to note that" | (just state the thing) |
| "in my opinion" | (just state the opinion) |
| "basically" | (delete) |
| "actually" | (delete unless genuinely contrasting) |
| "really" | (delete unless emphasizing measured quantity) |
| "very" | (find a stronger word) |
| "literally" | (delete unless literally literal) |
| "it should be noted that" | (just note it) |
| "as a matter of fact" | (delete) |
| "at the end of the day" | (delete) |
| "going forward" | (delete or use "next") |
| "leverage" (as verb) | "use" |
| "utilize" | "use" |

---

## Verb Upgrades

Replace vague/corporate verbs with concrete, vivid ones:

| Vague | Concrete alternatives |
|-------|----------------------|
| implement | build, ship, deploy, add, wire up |
| utilize | use |
| facilitate | enable, let, help, allow |
| leverage | use, apply, build on |
| optimize | speed up, shrink, cut, tune, tighten |
| ensure | check, verify, confirm, guarantee |
| impact (verb) | affect, change, break, improve, hurt |
| interface with | talk to, call, connect to |
| iterate on | revise, rework, refine, improve |
| synergize | (find what you actually mean) |

---

## Scannability Design

Busy experts skim in 30 seconds. Design for them:

### Subheadings
- **Descriptive:** "Why LLM Latency Spikes at Night" ✅
- **Generic:** "Challenges" ❌
- **Descriptive:** "Three Configs That Prevent Drift" ✅
- **Generic:** "Solutions" ❌

### Visual Hierarchy
- **Bold key terms** on first use
- **Bullets** for parallel items (3+ similar things)
- **Numbered lists** for sequential steps
- **Tables** for comparisons
- **Code blocks** for anything technical
- **Pull quotes** for key insights in long pieces

### Inverted Pyramid
Put key results and conclusions **early**, not buried at the end. Details can follow for readers who want depth.

Think of this as caching: surface the "indices" and key results up front; details can be streamed as needed.

---

## Before/After Rewrites

### Example 1: Corporate Fluff → Clear Statement

**Before** (38 words):
> In order to ensure that our deployment pipeline is optimized for maximum efficiency, it is important to note that we should leverage containerization technologies to facilitate the implementation of continuous integration and continuous delivery workflows.

**After** (16 words):
> Use containers to build a CI/CD pipeline. Here's how we set ours up.

### Example 2: Abstract → Concrete

**Before** (29 words):
> We implemented a comprehensive monitoring solution that enabled us to gain visibility into our system's performance characteristics and identify areas for potential optimization across multiple dimensions.

**After** (22 words):
> We added Prometheus and Grafana dashboards that track p50/p95/p99 latency, error rates, and CPU utilization per service. Here's the config.

### Example 3: Passive → Active

**Before** (19 words):
> It was determined by the team that the database migration should be performed during the maintenance window on Saturday.

**After** (13 words):
> The team decided to run the database migration during Saturday's maintenance window.

---

## The Complexity Paradox

**Simple writing ≠ simplistic thinking.**

Research confirms you can discuss complex topics *and* gain engagement if the language itself is easy to parse. The cognitive load should be in the *ideas*, not in decoding the sentences.

| Aspect | Make it simple | Keep it complex |
|--------|---------------|-----------------|
| Sentence structure | ✅ Short, clear | ❌ Nested clauses |
| Vocabulary | ✅ Common words | ❌ Unnecessary jargon |
| Ideas | ❌ Don't oversimplify | ✅ Full nuance |
| Technical depth | ❌ Don't water down | ✅ Real details |
| Examples | ✅ Concrete, specific | ❌ Abstract hand-waving |

**The goal:** A smart but tired reader should never have to re-read a sentence to understand it. If they re-read, it should be because the *idea* is worth thinking about, not because the *writing* is unclear.
