export const meta = {
  name: 'ocr',
  description:
    'On-device OCR of scanned documents (auge / Apple Vision, auto-rotating) followed by ' +
    'parallel Opus classification into a reviewable rename/sort proposal. Produces only a ' +
    'proposal — nothing is moved; applying is a separate, human-gated step.',
  phases: [
    { title: 'OCR' },
    { title: 'Classify', model: 'opus' },
    { title: 'Proposal' },
  ],
}

// ---------------------------------------------------------------------------
// args (passed by the /ocr command or the document-ocr skill):
//   pluginRoot  ${CLAUDE_PLUGIN_ROOT} — where the bundled scripts live
//   scanDir     absolute path to the folder of scans (jpg/png/pdf/heic/...)
//   outDir      where the OCR text + proposal go (default: <scanDir>_ocr)
//   context     user-provided CONTEXT — who-is-who, document types, target
//               taxonomy (folders), naming convention. Generic, never shipped;
//               it is the biggest quality lever and is supplied per run. Empty
//               is allowed (more conservative classification).
//   langs       OCR language hints (BCP-47, e.g. 'de-DE,en-US')
//   model       classification model (default 'opus')
// ---------------------------------------------------------------------------
const a = (typeof args === 'object' && args) ? args : {}
const pluginRoot = a.pluginRoot || '.'
const scanDir = a.scanDir || ''
const outDir = a.outDir || (String(scanDir).replace(/\/+$/, '') + '_ocr')
const context = (a.context && String(a.context).trim()) ? String(a.context).trim()
  : '(Kein Kontext angegeben. Ordne konservativ ein; person/datum im Zweifel "unbekannt".)'
const langs = a.langs || 'de-DE,en-US'
const model = a.model || 'opus'

if (!scanDir) {
  log('No scan folder in args.scanDir — nothing to do.')
  return { error: 'missing args.scanDir' }
}

const sh = (s) => "'" + String(s).replace(/'/g, "'\\''") + "'"

// ===========================================================================
// Phase 1 — OCR (auge / Apple Vision), on-device, auto-rotating
// ===========================================================================
phase('OCR')
const OCR_SCHEMA = {
  type: 'object',
  required: ['outDir', 'sessions'],
  properties: {
    outDir: { type: 'string' },
    sessions: {
      type: 'array',
      items: {
        type: 'object', required: ['session', 'file'],
        properties: { session: { type: 'string' }, file: { type: 'string' } },
      },
    },
  },
}
const ocr = await agent([
  'Run the bundled on-device OCR step. Do not classify or interpret content here.',
  '  OCR_LANGS=' + sh(langs) + ' uv run ' + sh(pluginRoot + '/scripts/ocr.py') + ' ' + sh(scanDir) + ' ' + sh(outDir),
  'This writes one <session>.txt per document into the output dir (auge auto-rotates',
  'scans and returns "no text detected" for pure photos — that is fine).',
  'Then list the resulting *.txt files (excluding names starting with "_") and return',
  'the output dir plus one {session, file} per document (session = filename without .txt).',
].join('\n'), { label: 'ocr', phase: 'OCR', model: 'haiku', schema: OCR_SCHEMA })

if (!ocr || !(ocr.sessions || []).length) {
  log('OCR produced no documents — aborting.')
  return { error: 'no documents', ocr }
}
log('OCR done: ' + ocr.sessions.length + ' document(s).')

// ===========================================================================
// Phase 2 — classify each document in parallel (Opus), shared generic prompt
// ===========================================================================
phase('Classify')
const CLS_SCHEMA = {
  type: 'object',
  required: ['session', 'dokumenttyp', 'person', 'datum', 'sprechender_name', 'zielordner', 'konfidenz', 'ist_muell', 'begruendung'],
  properties: {
    session: { type: 'string' },
    dokumenttyp: { type: 'string' },
    person: { type: 'string' },
    datum: { type: 'string' },
    sprechender_name: { type: 'string' },
    zielordner: { type: 'string' },
    konfidenz: { type: 'string', enum: ['hoch', 'mittel', 'niedrig'] },
    ist_muell: { type: 'boolean' },
    begruendung: { type: 'string' },
  },
}
const classified = await parallel(ocr.sessions.map((s) => () =>
  agent([
    'Classify ONE scanned document. Read these two files:',
    '  - the generic task + JSON schema: ' + pluginRoot + '/scripts/classify_prompt.md',
    '  - the OCR text of this document:  ' + s.file,
    '',
    'KONTEXT (user-provided — who-is-who, document types, target taxonomy, naming',
    'convention). Use ONLY this; invent nothing it does not support:',
    '---',
    context,
    '---',
    '',
    'Apply the task from classify_prompt.md to the OCR text under that KONTEXT and',
    'return the JSON object it specifies. Set "session" to ' + JSON.stringify(s.session) + '.',
    'Do not write any file in this step — just return the object.',
  ].join('\n'), { label: 'classify:' + s.session, phase: 'Classify', model: model, schema: CLS_SCHEMA })
    .then((r) => r)
    .catch(() => ({
      session: s.session, dokumenttyp: 'ERROR', person: 'unbekannt', datum: 'unbekannt',
      sprechender_name: s.session, zielordner: '', konfidenz: 'niedrig', ist_muell: false,
      begruendung: 'classification failed',
    }))
))
const results = classified.filter(Boolean)
const low = results.filter((r) => r.konfidenz === 'niedrig').length
log('Classified ' + results.length + '/' + ocr.sessions.length + ' (' + low + ' low confidence).')

// ===========================================================================
// Phase 3 — assemble the reviewable proposal (no moves)
// ===========================================================================
phase('Proposal')
const proposalJson = ocr.outDir + '/_vorschlag.json'
const proposalMd = ocr.outDir + '/_vorschlag.md'
await agent([
  'Write the OCR classification proposal from the data below. Two files, no moves.',
  '',
  '1. Write this JSON array verbatim to ' + proposalJson + ':',
  '```json',
  JSON.stringify(results, null, 2),
  '```',
  '',
  '2. Write a human review table to ' + proposalMd + ': a Markdown header noting the',
  '   source dir and document count, the line "Review, correct _vorschlag.json if',
  '   needed, then run /ocr-apply (dry-run first).", then a table with columns',
  '   ID | Type | Person | Date | speaking name | target folder | confidence | trash,',
  '   one row per entry (trash = mark if ist_muell). After the table, list any',
  '   low-confidence entries (konfidenz = niedrig) with their begruendung.',
  '',
  'Return the two paths.',
].join('\n'), { label: 'assemble-proposal', phase: 'Proposal', model: 'haiku' })

return {
  outDir: ocr.outDir,
  proposalJson,
  proposalMd,
  documents: results.length,
  lowConfidence: low,
  results,
  nextStep: 'Review ' + proposalMd + ', then /ocr-apply (dry-run by default) to move files.',
}
