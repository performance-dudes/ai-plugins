# The five context-aware patterns

The repeatable moves that make a plugin's workflows and agents context-aware.
Each is shown as a problem → pattern → concrete shape. The demo workflow
`workflows/context-aware-demo.js` implements all five.

## Contents

- 1. Index-once-slice-many
- 2. Fetch-and-index (never WebFetch into the window)
- 3. Plain-JS glue (deterministic, zero model tokens)
- 4. Structured-output handoffs (lean JSON, not prose)
- 5. Lean orchestrator (the workflow is code, not an agent)
- How they compose

---

## 1. Index-once-slice-many

**Problem.** N agents each need the same big reference (a profile, ruleset, spec,
SKILL). If each `Read`s it, you pay for the whole file N times.

**Pattern.** Index every reference **once** under a labelled `source`, in a
dedicated early phase. Every downstream agent then pulls only the ~200-token slice
it needs with `ctx_search`, scoped by `source`.

```js
// Phase "Index" — once, in the workflow
await agent(
  `Index these reference files into context-mode — one ctx_index call each (path + source).
   Return only "indexed: ok":
     ctx_index({ path: "${root}/skills/.../profile.md", source: "ref:profile" })
     ctx_index({ path: "${root}/skills/.../ruleset.md", source: "ref:ruleset" })`,
  { label: "index-refs", phase: "Index" }
)

// Every later agent prompt carries this instead of file contents:
const READ = `Pull what you need from context-mode (references are PRE-INDEXED — do NOT Read the
whole files, that bloats the window). One bundled ctx_search call, scope by source:
  ref:profile  (the requirements)
  ref:ruleset  (the rules)
Fallback only if ctx_search returns empty: Read the specific file.`
```

**Payoff.** `1 × index + N × slice` instead of `N × whole-file`. For a 4 KB
reference and 60 agents that is ≈16 K tokens instead of ≈240 K — ~15×.

---

## 2. Fetch-and-index (never WebFetch into the window)

**Problem.** A web page or API doc is 50–100 KB of HTML. `WebFetch` drops all of
it into the conversation; you needed three facts.

**Pattern.** `ctx_fetch_and_index` the URL (HTML → markdown → chunked → FTS5),
then `ctx_search` the derived answer out. The page bytes stay in the sandbox.

```js
// in an agent's system prompt:
// "Load every URL with ctx_fetch_and_index (source: a stable label per page),
//  then ctx_search the facts you need. NEVER WebFetch or Read raw HTML into the window."
ctx_fetch_and_index({ requests: [{ url, source: "page:" + id }], concurrency: 4 })
ctx_search({ queries: ["price", "size", "build year"], source: "page:" + id })
```

**Payoff.** The conversation sees a handful of fields, not the page. Cache (TTL,
default 24h) makes re-queries free.

---

## 3. Plain-JS glue (deterministic, zero model tokens)

**Problem.** Dedup, fingerprinting, filtering, ranking, ledger bookkeeping — work
an LLM *can* do but shouldn't: it is slow, non-reproducible, and burns tokens
"thinking".

**Pattern.** Do it as **code** in the workflow (or in `ctx_execute`). The model is
reserved for judgement that genuinely needs a model.

```js
// Dedup by fingerprint — plain JS, no agent. (demo: see the DEDUP block)
const fp = (f) => `${norm(f.source)}|${norm(f.claim).slice(0, 60)}`
const byFp = new Map()
for (const f of allFindings) {
  const k = fp(f)
  const prev = byFp.get(k)
  if (!prev) { byFp.set(k, { ...f, seen: 1 }); continue }
  prev.seen++                                   // merge duplicates
  if ((f.confidence || 0) > (prev.confidence || 0)) prev.confidence = f.confidence
}
const deduped = [...byFp.values()].sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
```

**Payoff.** Free, auditable, identical every run. The workflow itself accumulates
no transcript, so this code is ≈0 tokens.

---

## 4. Structured-output handoffs (lean JSON, not prose)

**Problem.** If phase N returns a paragraph and phase N+1 reads it, the handoff is
seedy and the next agent re-reasons over prose.

**Pattern.** Force each agent to a **schema** with the `schema` option. `agent()`
returns the validated object; the next phase reads only the fields it needs.

```js
const FINDINGS_SCHEMA = {
  type: "object", required: ["findings"], additionalProperties: false,
  properties: {
    findings: { type: "array", items: {
      type: "object", additionalProperties: false,
      required: ["claim", "source", "confidence", "fingerprint"],
      properties: {
        claim:       { type: "string" },
        source:      { type: "string" },
        confidence:  { type: "number" },          // 0..1
        fingerprint: { type: "string" },          // for plain-JS dedup
      },
    } },
  },
}
const out = await agent(prompt, { schema: FINDINGS_SCHEMA, label: "scout" })
// out.findings is validated — no parsing, no prose
```

**Payoff.** Tiny, machine-checkable handoffs. The schema also makes the agent
emit the `fingerprint` that pattern 3 dedups on — the patterns compose.

---

## 5. Lean orchestrator (the workflow is code, not an agent)

**Problem.** A single "manager" agent that calls sub-agents accumulates every
sub-result in its own growing transcript → quadratic cost.

**Pattern.** The orchestration lives in a **deterministic JS workflow**. It
`phase()`s, `parallel()`/`pipeline()`s, fans out with `agent()`, dedups in JS, and
`return`s a structured object. It has **no model context** of its own. Each
`agent()` runs in a **fresh window** and gets back only lean JSON.

```
workflow (plain JS, ≈0 tokens)
  phase Index    → 1 agent indexes refs + fetches URLs (raw bytes → sandbox)
  phase Scout    → parallel( one agent per sub-question )   → FINDINGS_SCHEMA
  dedup          → plain JS (pattern 3)
  phase Synth    → 1 agent reads deduped JSON, ctx_search for gaps → REPORT_SCHEMA
  return { report }
```

Prefer `pipeline()` (no barrier between stages) by default; use `parallel()` only
when a stage genuinely needs all prior results at once (e.g. a global dedup before
synthesis — which is exactly the demo's shape).

**Payoff.** Model tokens fall only in the leaves, and the leaves are kept small by
patterns 1–4. The orchestrator scales to dozens of agents without its own context
growing.

---

## How they compose

```
  index once ─────────────┐
  fetch-and-index ────────┤→ leaf agents see only SLICES (vertical savings)
                          │
  fan out (lean orch) ────┤→ fresh window per agent      (horizontal savings)
  schema handoffs ────────┤→ phases exchange tiny JSON
  plain-JS glue ──────────┘→ dedup/rank/ledger cost 0 model tokens
```

Vertical (1, 2) shrinks what each agent sees. Horizontal (5) stops agents paying
for each other. Schemas (4) keep the seams between phases tiny, and JS glue (3)
keeps the deterministic work out of the model entirely. Adopt them in that order
of payoff.
