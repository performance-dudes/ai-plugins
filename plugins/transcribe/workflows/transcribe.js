export const meta = {
  name: 'transcribe',
  description: 'Quality-first multi-speaker transcription: deterministic on-device pipeline (ffmpeg -> Whisper -> pyannote -> merge) followed by parallel Opus deliverables (verbatim clean transcript, minutes, quoted facts, personas, todos).',
  phases: [
    { title: 'Pipeline' },
    { title: 'Chunk' },
    { title: 'Clean transcript', model: 'opus' },
    { title: 'Deliverables', model: 'opus' },
  ],
}

// ---------------------------------------------------------------------------
// args (passed by the /transcribe command or the transcription skill):
//   pluginRoot   ${CLAUDE_PLUGIN_ROOT} — where the bundled scripts live. Optional:
//                if absent (e.g. the workflow was run directly by name) the pipeline
//                agent self-resolves the bundled scripts dir, so nothing breaks.
//   audio        absolute path to the audio/video file
//   numSpeakers  known speaker count (string/number) or '' for auto
//   locale       BCP-47 locale of the conversation, e.g. 'de-DE' (default de-DE)
//   context      user-provided CONTEXT block — occasion, participants, names and
//                their typical mis-transcriptions, domain terms. Generic, never
//                shipped: it is the single biggest quality lever and is supplied
//                per conversation by the user. Empty is allowed (fewer corrections).
//   speakerMap   optional pre-known 'SPEAKER_00=Name SPEAKER_01=Name' (string)
// ---------------------------------------------------------------------------
// `args` may arrive three ways — all must land, so a mis-shaped invocation never
// hard-fails a 40-minute job:
//   1. a parsed object     — the /transcribe command and the skill pass structured args.
//   2. a JSON string       — the Workflow runtime serialises an object.
//   3. a free-text brief   — running the workflow directly (e.g. /transcribe:transcribe)
//      hands us the raw $ARGUMENTS text. Parse the media path, locale and speaker count
//      out of it and keep the whole brief as context; pluginRoot is then unknown and the
//      pipeline agent self-resolves the bundled scripts dir (see Phase 1).
const MEDIA_EXT = 'mp3|m4a|wav|flac|aac|ogg|opus|aiff?|wma|mp4|mkv|mov|webm|m4v|avi|mpe?g'
function parseStringArgs(s) {
  const out = { context: s }
  const p = s.match(new RegExp('(\\/[^\\s"\'`)]+\\.(?:' + MEDIA_EXT + '))', 'i'))   // absolute path first
    || s.match(new RegExp('([^\\s"\'`)]+\\.(?:' + MEDIA_EXT + '))', 'i'))            // else any media path
  if (p) out.audio = p[1]
  const bcp = s.match(/\b([a-z]{2}-[A-Z]{2})\b/)                                     // explicit BCP-47 wins
  if (bcp) out.locale = bcp[1]
  else if (/\b(deutsch|german)\b/i.test(s) || /\b(?:sprache|locale|language)\s*[:=]?\s*de\b/i.test(s)) out.locale = 'de-DE'
  else if (/\b(englisch|english)\b/i.test(s) || /\b(?:sprache|locale|language)\s*[:=]?\s*en\b/i.test(s)) out.locale = 'en-US'
  const spk = s.match(/\b(\d{1,2})\s*(?:speakers?|sprecher\w*|stimmen|personen|teilnehmer\w*)\b/i)
    || s.match(/\b(?:num[_\s]?speakers?|speakers?|sprecher(?:zahl)?)\s*[:=]?\s*(\d{1,2})\b/i)
  if (spk) out.numSpeakers = spk[1]
  return out
}
const a = (args && typeof args === 'object') ? args
  : (typeof args === 'string' && args.trim())
    ? (() => { const t = args.trim(); if (t[0] === '{' || t[0] === '[') { try { return JSON.parse(t) } catch (e) { /* not JSON — treat as brief */ } } return parseStringArgs(t) })()
    : {}
const pluginRoot = a.pluginRoot || ''
const scriptsDir = pluginRoot ? (pluginRoot + '/scripts') : ''   // '' → pipeline agent self-resolves
const audio = a.audio || ''
const numSpeakers = (a.numSpeakers === undefined || a.numSpeakers === null || a.numSpeakers === '') ? '' : String(a.numSpeakers)
const locale = a.locale || 'de-DE'
const context = (a.context && String(a.context).trim()) ? String(a.context).trim()
  : '(Kein zusätzlicher Kontext angegeben. Korrigiere keine Eigennamen ohne Beleg.)'
const presetMap = (a.speakerMap && String(a.speakerMap).trim()) ? String(a.speakerMap).trim() : ''

if (!audio) {
  log('No audio path found in args (neither args.audio nor a media path in the brief).')
  return { error: 'missing audio path', hint: 'Pass args.audio as an absolute path, or include a media file path in the text.' }
}

const sh = (s) => "'" + String(s).replace(/'/g, "'\\''") + "'" // single-quote for bash

// ---- prompt builders (generic, context-driven, no hardcoded names) --------

function contextHeader() {
  return [
    'KONTEXT (vom Nutzer bereitgestellt — Anlass, Teilnehmer, Eigennamen und ihre',
    'typischen Falschschreibungen, Fachbegriffe). Sprache des Gesprächs: ' + locale + '.',
    '',
    context,
    '',
  ].join('\n')
}

// Strict verbatim clean-transcript task with per-chunk anchors. Mirrors the
// empirically-validated "Opus + strict + anchors" prompt, but every example is
// generic: corrections come ONLY from the user CONTEXT above.
function buildCleanTask(m) {
  return [
    'AUFGABE: Erzeuge ein 1:1-WORTGETREUES Transkript aus dem Rohtranskript-Chunk unten.',
    '',
    'HARTE REGELN (jeder Verstoß = Aufgabe nicht erledigt):',
    '',
    '1. VOLLSTÄNDIGKEIT IST PFLICHT. Lass KEINE Sätze, Sprechertrennungen, Wiederholungen,',
    '   Begrüßungen, Vorstellungen, Smalltalk oder nebensächliche Passagen weg.',
    '',
    '2. EXAKTE TURN-ANZAHL. Der Input enthält ' + m.turn_count + ' Zeitstempel-Blöcke',
    '   [HH:MM:SS] Sprecher: Text. Dein Output MUSS exakt ' + m.turn_count + ' Blöcke enthalten —',
    '   keine Konsolidierung, keine Zusammenfassung, kein Skippen.',
    '',
    '3. EXAKTER START. Dein Output beginnt mit der Zeile [' + m.first_ts + '] ' + m.first_speaker + ': …',
    '',
    '4. EXAKTES ENDE. Dein Output endet mit dem Block [' + m.last_ts + '] ' + m.last_speaker + ': …',
    '',
    '5. OUTPUT-LÄNGE MINDESTENS 85 % DER INPUT-LÄNGE. Input ist ~' + m.input_chars + ' Zeichen,',
    '   Output also mindestens ~' + m.min_output_chars + ' Zeichen. Kürzer = komprimiert = falsch.',
    '',
    '6. ZEITSTEMPEL UNVERÄNDERT ÜBERNEHMEN im Format [HH:MM:SS]. Nicht zusammenlegen.',
    '',
    '7. WAS DU ÄNDERN DARFST (und sollst):',
    '   - Verstümmelte Eigennamen und Fachbegriffe NUR anhand des KONTEXTS korrigieren: nennt der',
    '     KONTEXT einen Namen samt typischer Falschschreibung, ersetze die Falschschreibung durch',
    '     die korrekte Form. Liegt zu einem Begriff KEIN Kontext vor, NICHT raten — Original behalten.',
    '   - Sprecher-Pseudonyme (SPEAKER_NN) sind im Input bereits zu Namen aufgelöst; prüfe nur',
    '     grobe Mismatches gegen den Inhalt und markiere sie mit (Name?) statt still umzuschreiben.',
    '   - Satzzeichen ergänzen, offensichtliche Tippfehler korrigieren.',
    '   - Transkriptions-Halluzinationen am Audio-Ende (z. B. wiederholte Abschiedsfloskeln) entfernen.',
    '',
    '8. WAS DU NICHT ÄNDERN DARFST: nichts zusammenfassen, paraphrasieren oder kürzen; keine',
    '   Inhalte weglassen; keine eigenen Kommentare, Meta-Bemerkungen oder Vorworte.',
    '',
    '9. OUTPUT-FORMAT pro Block: [HH:MM:SS] Name: Text — exakt wie Input, nur mit',
    '   Eigennamen-Korrekturen. Kein Vorspann, kein Header, keine Code-Fences.',
    '',
    '10. SELF-CHECK VOR ANTWORT: Hat dein Output ' + m.turn_count + ' Blöcke? Beginnt er mit',
    '    [' + m.first_ts + ']? Endet er mit [' + m.last_ts + ']? Mindestens ' + m.min_output_chars + ' Zeichen?',
    '    Wenn nein, fülle nach.',
  ].join('\n')
}

// Deliverables run on the assembled clean transcript. All generic.
const DELIVERABLES = [
  {
    key: 'protokoll', file: 'protokoll.md',
    task: [
      'AUFGABE: Schreibe ein nüchternes Protokoll des Gesprächs.',
      '',
      'GLIEDERUNG: 1. Teilnehmer & Anlass  2. Verlauf (chronologisch, Stichpunkte)',
      '3. Zentrale Fakten & Entscheidungen  4. Zusagen, Next Steps.',
      '',
      'REGELN: Nur was im Transkript gesagt wurde, keine Interpretation oder Bewertung.',
      'Sachlich, präzise, Markdown. Wo hilfreich: Zeitstempel-Verweise [HH:MM:SS].',
    ].join('\n'),
  },
  {
    key: 'fakten', file: 'fakten_mit_zitaten.md',
    task: [
      'AUFGABE: Liste die wichtigsten Fakten aus dem Gespräch.',
      '',
      'STRIKTE REGELN:',
      '- Jeder Fakt MUSS mit wörtlichem Zitat belegt sein, Format: [HH:MM:SS] Sprecher: "Zitat".',
      '- Zitate exakt aus dem Transkript übernehmen (keine Paraphrase).',
      '- Kein passendes Zitat → Fakt weglassen.',
      '- Bei vermuteten Transkriptionsfehlern mit [?] kennzeichnen.',
      '- Sachlich, präzise, Markdown mit Tabellen wo sinnvoll.',
    ].join('\n'),
  },
  {
    key: 'personas', file: 'personas.md',
    task: [
      'AUFGABE: Steckbriefe aller im Gespräch genannten Personen.',
      '',
      'PRO PERSON: Name (korrigierte Form aus KONTEXT) · Rolle/Firma falls erwähnt ·',
      'was über die Person gesagt wurde (mit Zitat-Beleg [HH:MM:SS]) · Bezug zu den Teilnehmern.',
      '',
      'REGELN: Nur was im Transkript steht, nichts erfinden. Kein Punkt ohne Zitat-Beleg.',
    ].join('\n'),
  },
  {
    key: 'todos', file: 'todos.md',
    task: [
      'AUFGABE: Liste alle expliziten Zusagen, Next Steps und offenen Punkte.',
      '',
      'PRO EINTRAG: Wer (Sprecher) · Was (Aufgabe) · Bis wann (falls erwähnt) ·',
      'Beleg: [HH:MM:SS] Sprecher: "Zitat".',
      '',
      'REGELN: Nur explizit zugesagte/vereinbarte Punkte. Kein Eintrag ohne Zitat-Beleg.',
      'Markdown-Liste oder Tabelle.',
    ].join('\n'),
  },
]

// ===========================================================================
// Phase 1 — deterministic on-device pipeline + speaker proposal
// ===========================================================================
phase('Pipeline')
const PIPELINE_SCHEMA = {
  type: 'object',
  required: ['stem', 'outDir', 'mergedRaw', 'totalTurns', 'proposedMap', 'scriptsDir'],
  properties: {
    stem: { type: 'string', description: 'absolute path of the audio without extension' },
    outDir: { type: 'string', description: 'absolute deliverables dir <stem>_transkript' },
    mergedRaw: { type: 'string', description: 'absolute path of <stem>_merged_raw.json' },
    scriptsDir: { type: 'string', description: 'absolute path of the bundled transcribe scripts dir actually used' },
    totalTurns: { type: 'number' },
    proposedMap: {
      type: 'array', description: 'proposed speaker-id to real-name mapping',
      items: {
        type: 'object', required: ['id', 'name'],
        properties: { id: { type: 'string' }, name: { type: 'string' }, evidence: { type: 'string' } },
      },
    },
  },
}

// Path to a bundled script. When scriptsDir is known, a literal quoted path; when
// unknown (no pluginRoot), a <SCRIPTS> placeholder the agent fills after resolving.
const scriptRef = (name) => scriptsDir ? sh(scriptsDir + '/' + name) : ('"<SCRIPTS>/' + name + '"')

const pipeline = await agent([
  'Run the bundled, deterministic, on-device transcription pipeline. Do NOT summarise or',
  'interpret content in this step — only run scripts and read structure.',
  '',
  scriptsDir
    ? ('Bundled scripts directory: ' + scriptsDir)
    : ['This run supplied no pluginRoot — resolve the bundled scripts directory FIRST:',
       '  ls -d "$HOME"/.claude/plugins/marketplaces/*/plugins/transcribe/scripts "$HOME"/.claude/plugins/cache/*/transcribe/*/scripts 2>/dev/null | sort -V | tail -1',
       'Take that absolute path as <SCRIPTS> and substitute it directly into every command',
       'below (shell variables do NOT persist between separate Bash calls, so use the concrete',
       'path each time). If nothing is found, tell the user to run /transcribe-doctor and stop.'].join('\n'),
  '',
  'Steps (run each with a generous Bash timeout; the script is idempotent and resumes):',
  '1. Phases 1-3 (ffmpeg -> Whisper -> pyannote):',
  '     bash ' + scriptRef('run_pipeline.sh') + ' ' + sh(audio) + (numSpeakers ? ' ' + sh(numSpeakers) : ''),
  '2. Phase 4 (mechanical merge of transcript x speaker segments), no map yet:',
  '     uv run ' + scriptRef('merge.py') + ' "<stem>"',
  '   where <stem> is the audio path without its extension.',
  '3. Read the first ~8 minutes of "<stem>_merged.txt". From self-introductions propose a',
  '   mapping SPEAKER_00 -> real name. If a speaker never identifies themselves, map them to a',
  '   neutral label like "Sprecher A". Record one short evidence quote per mapping.',
  presetMap ? ('   A pre-known mapping was supplied, prefer it: ' + presetMap) : '',
  '',
  'Return the stem, the deliverables dir "<stem>_transkript", the merged_raw path, the total',
  'block count, the proposed map, and the resolved bundled scripts dir as "scriptsDir"',
  '(' + (scriptsDir ? 'it is ' + scriptsDir : 'the <SCRIPTS> path you resolved') + '). Create the deliverables dir (mkdir -p) if missing.',
].join('\n'), { label: 'pipeline+speaker-id', phase: 'Pipeline', model: 'sonnet', schema: PIPELINE_SCHEMA })

if (!pipeline || !pipeline.mergedRaw) {
  log('Pipeline phase failed — aborting.')
  return { error: 'pipeline failed', pipeline }
}
const mapArgs = (pipeline.proposedMap || []).map((p) => sh(p.id + '=' + p.name)).join(' ')
log('Pipeline done: ' + pipeline.totalTurns + ' turns, ' + (pipeline.proposedMap || []).length + ' speakers proposed.')

// ===========================================================================
// Phase 2 — chunk the merged transcript into strict-pass windows
// ===========================================================================
phase('Chunk')
const MANIFEST_SCHEMA = {
  type: 'object', required: ['chunks'],
  properties: {
    chunks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['index', 'file', 'turn_count', 'first_ts', 'first_speaker', 'last_ts', 'last_speaker', 'input_chars', 'min_output_chars'],
        properties: {
          index: { type: 'number' }, file: { type: 'string' },
          turn_count: { type: 'number' }, first_ts: { type: 'string' }, first_speaker: { type: 'string' },
          last_ts: { type: 'string' }, last_speaker: { type: 'string' },
          input_chars: { type: 'number' }, min_output_chars: { type: 'number' },
        },
      },
    },
  },
}
// Reuse the scripts dir the pipeline agent actually used (resolved even without pluginRoot).
const scriptsDirResolved = pipeline.scriptsDir || scriptsDir
const chunkResult = await agent([
  'Run the bundled chunker, then return its manifest verbatim.',
  '  uv run ' + sh(scriptsDirResolved + '/prepare_chunks.py') + ' ' + sh(pipeline.mergedRaw) +
    (mapArgs ? ' --map ' + mapArgs : '') + ' --out ' + sh(pipeline.outDir),
  'Then read "' + pipeline.outDir + '/chunks/manifest.json" and return its array as {chunks: [...]}.',
].join('\n'), { label: 'chunk', phase: 'Chunk', model: 'haiku', schema: MANIFEST_SCHEMA })

const chunks = (chunkResult && chunkResult.chunks) || []
if (!chunks.length) {
  log('Chunking produced no chunks — aborting.')
  return { error: 'no chunks', pipeline }
}
log('Chunked into ' + chunks.length + ' window(s) for the strict clean pass.')

// ===========================================================================
// Phase 3 — strict verbatim clean transcript, one Opus agent per chunk (parallel)
// ===========================================================================
phase('Clean transcript')
const ctxHead = contextHeader()
const cleaned = await parallel(chunks.map((m) => () =>
  agent([
    ctxHead,
    'ROHTRANSKRIPT-CHUNK (Whisper + pyannote, Sprecher bereits gemappt) — lies die Datei:',
    '  ' + m.file,
    '',
    buildCleanTask(m),
    '',
    'Schreibe NUR das bereinigte Transkript nach: ' + pipeline.outDir + '/chunks/clean_' +
      String(m.index).padStart(2, '0') + '.md',
    'Gib als finale Nachricht ausschließlich diesen Output-Pfad zurück.',
  ].join('\n'), { label: 'clean:chunk_' + m.index, phase: 'Clean transcript', model: 'opus' })
    .then((r) => ({ index: m.index, ok: !!r }))
    .catch(() => ({ index: m.index, ok: false }))
))
const cleanOk = cleaned.filter((c) => c && c.ok).length
log('Clean transcript: ' + cleanOk + '/' + chunks.length + ' chunks done.')

// Assemble the chunk clean files (in order) into the final clean transcript.
const cleanPath = pipeline.outDir + '/transkript_clean.md'
await agent([
  'Concatenate the per-chunk clean files in ascending index order into one file.',
  '  for f in ' + sh(pipeline.outDir + '/chunks') + '/clean_*.md; do cat "$f"; echo; done > ' + sh(cleanPath),
  'Verify the result is non-empty. Return the path.',
].join('\n'), { label: 'assemble-clean', phase: 'Clean transcript', model: 'haiku' })

// ===========================================================================
// Phase 4 — deliverables on the clean transcript, in parallel (Opus)
// ===========================================================================
phase('Deliverables')
const delivered = await parallel(DELIVERABLES.map((d) => () =>
  agent([
    ctxHead,
    'BEREINIGTES TRANSKRIPT — lies die Datei:',
    '  ' + cleanPath,
    '',
    d.task,
    '',
    'Schreibe das Ergebnis als Markdown nach: ' + pipeline.outDir + '/' + d.file,
    'Gib als finale Nachricht ausschließlich diesen Output-Pfad zurück.',
  ].join('\n'), { label: 'deliverable:' + d.key, phase: 'Deliverables', model: 'opus' })
    .then((r) => ({ key: d.key, ok: !!r }))
    .catch(() => ({ key: d.key, ok: false }))
))
const delivOk = delivered.filter((d) => d && d.ok).length
log('Deliverables: ' + delivOk + '/' + DELIVERABLES.length + ' done.')

return {
  outDir: pipeline.outDir,
  cleanTranscript: cleanPath,
  deliverables: DELIVERABLES.map((d) => pipeline.outDir + '/' + d.file),
  chunks: chunks.length,
  proposedMap: pipeline.proposedMap || [],
  totalTurns: pipeline.totalTurns,
}
