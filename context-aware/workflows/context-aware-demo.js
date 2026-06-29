export const meta = {
  name: 'context-aware-demo',
  description:
    'Runnable reference implementation of the five context-aware patterns. Indexes the given files (ctx_index) and URLs (ctx_fetch_and_index) ONCE into context-mode and plans sub-questions (Index), fans out one scout agent per sub-question that pulls only ctx_search slices (Scout), dedups their findings in plain JS, then synthesizes a structured report that ctx_search-es only for gaps (Synthesize). No raw file or page bytes ever enter the conversation — all retrieval is routed through the bundled context-mode MCP (ctx_*).',
  phases: [
    { title: 'Index' },
    { title: 'Scout' },
    { title: 'Synthesize', model: 'opus' },
  ],
}

// ---------------------------------------------------------------------------
// args (from the /context-aware command or a calling harness):
//   pluginRoot  absolute path to this plugin dir
//   question    the research question (string)
//   files       array of file paths to index via ctx_index
//   urls        array of URLs to load via ctx_fetch_and_index
//   lanes       max parallel scouts / sub-questions (default 4)
// args may arrive as an object or a JSON string — handle both.
// ---------------------------------------------------------------------------
const a = (args && typeof args === 'object')
  ? args
  : (typeof args === 'string' && args.trim()
      ? (() => { try { return JSON.parse(args) } catch (e) { return {} } })()
      : {})

const pluginRoot = a.pluginRoot || '.'
const question = (a.question || '').trim() || 'Summarize the provided sources.'
const files = Array.isArray(a.files) ? a.files.filter(Boolean) : []
const urls = Array.isArray(a.urls) ? a.urls.filter(Boolean) : []
const lanes = Math.max(1, Math.min(8, Number(a.lanes) || 4))

// Stable source tags — these are the labels every agent scopes its ctx_search to.
const fileTags = files.map((p, i) => ({ tag: `src:file:${i}`, ref: p }))
const urlTags = urls.map((u, i) => ({ tag: `src:url:${i}`, ref: u }))
const allTags = [...fileTags, ...urlTags]
const tagList = allTags.map((t) => `  ${t.tag}  (${t.ref})`).join('\n') || '  (no sources provided)'

// The reusable retrieval-discipline block injected into every leaf agent.
const READ = `Pull everything from context-mode — the corpus is PRE-INDEXED (do NOT Read whole files or
WebFetch raw pages; that bloats the window). Use ctx_search, one bundled call, scope by these source tags:
${tagList}
If a needed URL is somehow not indexed, ctx_fetch_and_index it, then ctx_search. Use ctx_execute to
filter/parse. Never put raw bytes into your window.`

// ---------------------------------------------------------------------------
// Schemas — lean JSON handoffs between phases (pattern 4).
// ---------------------------------------------------------------------------
const PLAN_SCHEMA = {
  type: 'object', required: ['indexed', 'subquestions'], additionalProperties: false,
  properties: {
    indexed: { type: 'array', items: { type: 'string' } },        // source tags successfully indexed
    subquestions: { type: 'array', items: { type: 'string' } },   // decomposed from the question
  },
}

const FINDINGS_SCHEMA = {
  type: 'object', required: ['findings'], additionalProperties: false,
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['claim', 'source', 'confidence', 'fingerprint'],
        properties: {
          claim: { type: 'string' },
          source: { type: 'string' },            // which source tag / ref backs it
          confidence: { type: 'number' },        // 0..1
          fingerprint: { type: 'string' },       // source|claim-prefix — for plain-JS dedup
        },
      },
    },
  },
}

const REPORT_SCHEMA = {
  type: 'object', required: ['summary', 'key_points', 'gaps', 'sources_used'], additionalProperties: false,
  properties: {
    summary: { type: 'string' },
    key_points: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'string' } },
    sources_used: { type: 'array', items: { type: 'string' } },
  },
}

// ===========================================================================
// Phase 1 — INDEX: index files + fetch URLs ONCE, plan sub-questions.
// One leaf agent does the indexing so the raw bytes land in the sandbox, never
// here. It also proposes sub-questions because it has just seen the corpus.
// ===========================================================================
phase('Index')

const indexCalls = [
  ...fileTags.map((t) => `ctx_index({ path: ${JSON.stringify(t.ref)}, source: ${JSON.stringify(t.tag)} })`),
  ...urlTags.map((t) => `ctx_fetch_and_index({ url: ${JSON.stringify(t.ref)}, source: ${JSON.stringify(t.tag)} })`),
].join('\n')

const plan = await agent(
  `Index the corpus into context-mode, then plan the research.

Step 1 — run exactly these calls (one per source). Files via ctx_index, URLs via ctx_fetch_and_index:
${indexCalls || '(no sources — skip indexing)'}

Step 2 — decompose this question into up to ${lanes} focused, non-overlapping sub-questions that, answered
together, fully cover it. Fewer is fine.

QUESTION: ${question}

Return JSON: { "indexed": [<source tags you indexed ok>], "subquestions": [<the sub-questions>] }.
Do NOT dump file or page contents into your reply.`,
  { label: 'index+plan', phase: 'Index', schema: PLAN_SCHEMA },
).catch(() => null)

const subquestions = (plan && Array.isArray(plan.subquestions) && plan.subquestions.length
  ? plan.subquestions
  : [question]).slice(0, lanes)

log(`indexed ${plan && plan.indexed ? plan.indexed.length : 0}/${allTags.length} sources · ${subquestions.length} sub-questions`)

// ===========================================================================
// Phase 2 — SCOUT: one scout per sub-question, parallel. BARRIER here because
// the dedup step needs all findings together (a justified parallel()).
// ===========================================================================
phase('Scout')

const scouted = (await parallel(
  subquestions.map((q, i) => () =>
    agent(
      `${READ}\n\nYour sub-question (${i + 1}/${subquestions.length}): ${q}\n\nReport every supported finding as JSON.`,
      { label: `scout:${q.slice(0, 28)}`, phase: 'Scout', schema: FINDINGS_SCHEMA, agentType: 'context-scout' },
    ),
  ),
)).filter(Boolean)

const allFindings = scouted.flatMap((r) => (r && Array.isArray(r.findings) ? r.findings : []))

// ===========================================================================
// DEDUP — plain JS, no agent (pattern 3). Merge by fingerprint, keep the
// highest confidence, count how many scouts corroborated each claim.
// ===========================================================================
const norm = (s) => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim()
const fpOf = (f) => norm(f.fingerprint) || `${norm(f.source)}|${norm(f.claim).slice(0, 60)}`

const byFp = new Map()
for (const f of allFindings) {
  const k = fpOf(f)
  const prev = byFp.get(k)
  if (!prev) { byFp.set(k, { ...f, corroborations: 1 }); continue }
  prev.corroborations++
  if ((f.confidence || 0) > (prev.confidence || 0)) prev.confidence = f.confidence
  if ((f.claim || '').length > (prev.claim || '').length) prev.claim = f.claim
}
const deduped = [...byFp.values()].sort(
  (x, y) => (y.confidence || 0) - (x.confidence || 0) || (y.corroborations - x.corroborations),
)

log(`findings: ${allFindings.length} raw -> ${deduped.length} deduped`)

// ===========================================================================
// Phase 3 — SYNTHESIZE: one agent reads the lean deduped JSON, ctx_search only
// to fill gaps, returns a structured report.
// ===========================================================================
phase('Synthesize')

const report = await agent(
  `${READ}

QUESTION: ${question}

Deduped findings (lean JSON — your primary material; do NOT re-fetch the sources):
${JSON.stringify(deduped)}

Synthesize the answer. ctx_search the indexed corpus only to fill a specific gap. Return the report JSON.`,
  { label: 'synthesize', phase: 'Synthesize', schema: REPORT_SCHEMA, agentType: 'context-synthesizer' },
).catch(() => null)

return {
  question,
  report: report || { summary: '(synthesis failed)', key_points: [], gaps: ['synthesis agent returned nothing'], sources_used: [] },
  subquestions,
  sources: allTags.map((t) => ({ tag: t.tag, ref: t.ref })),
  findingsRaw: allFindings.length,
  findingsDeduped: deduped.length,
}
