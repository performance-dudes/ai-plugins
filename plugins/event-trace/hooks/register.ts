// event-trace — der Mod-Teil (Function-Hooks-Modul).
//
// Ein einziger Wildcard-Hook `on("*")` sieht JEDES Event der Engine: Engine-Events
// (tool.call, ui.render, prompt.submit, turn.step, turn.complete, ...), die
// klassischen Settings-Hook-Events als `classic.<Event>` und jeden Aufruf auf `$`
// — auch die der eingebauten Plugins (env.get, http.fetch, fs.read, ...).
// Telemetrie selektiert `*` nicht — dafür ein eigener Hook.
//
// Jeder Hook reicht unverändert weiter (`next(e)`), misst die Dauer bis die Kette
// darunter fertig ist und merkt sich das Ergebnis. Geschrieben wird gepuffert:
// ein Timer schreibt alle FLUSH_MS die laufende Datei neu
//   $EVENT_TRACE_DIR/<session>.mods.<load>-<part>.jsonl
// ($.fs.write kennt kein Append; ab PART_LINES Zeilen beginnt ein neuer Teil, so
// bleibt jeder Schreibvorgang klein und nichts geht verloren).

import type { EngineInterface, Register } from 'claude-code'

const FLUSH_MS = 1000
const PART_LINES = 2000
const MAX_FIELD = 1500
const SENSITIVE = /token|secret|password|passwd|api[-_]?key|authorization|cookie|credential|private[-_]?key/i

type Entry = {
  ts: string
  layer: 'mod'
  seq: number
  event: string
  origin: string
  ms: number
  outcome: 'ok' | 'deny' | 'error'
  input: unknown
  result?: unknown
}

// Werte unter sensibel benannten Schlüsseln (Header, Settings, Env) maskieren —
// der Tracer sieht alles, sein Log soll trotzdem keine Secrets enthalten.
const redact = (value: unknown, depth = 0): unknown => {
  if (depth > 12 || typeof value !== 'object' || value === null) return value
  if (Array.isArray(value)) return value.map(item => redact(item, depth + 1))
  return Object.fromEntries(
    Object.entries(value).map(([key, inner]) => [key, SENSITIVE.test(key) ? '[redacted]' : redact(inner, depth + 1)]),
  )
}

// Kurzfassung eines Werts: lange Payloads (ui.render, session.append, http.fetch)
// gekürzt, damit sie das Log nicht sprengen.
const clip = (value: unknown): unknown => {
  if (value === undefined) return undefined
  let text: string | undefined
  try {
    text = JSON.stringify(redact(value))
  } catch {
    return '[unserializable]'
  }
  if (text === undefined) return String(value)
  return text.length <= MAX_FIELD ? JSON.parse(text) : `${text.slice(0, MAX_FIELD)}… (+${text.length - MAX_FIELD} chars)`
}

const isDeny = (result: unknown): boolean =>
  typeof result === 'object' && result !== null && 'deny' in result && (result as { deny?: unknown }).deny !== undefined

// env.get liefert den Wert einer Umgebungsvariable — bei sensiblem Namen maskieren.
const isSecretRead = (event: string, e: unknown): boolean =>
  event === 'env.get' && typeof e === 'object' && e !== null && SENSITIVE.test(String((e as { name?: unknown }).name))

// Puffer + Zähler einer Modul-Ladung. Liegt in einem Objekt, weil `flush` als
// Top-Level-Funktion `$` bekommt (die Engine lässt `$` nur an solche übergeben).
type Trace = {
  load: string
  counts: Map<string, number>
  lines: string[]
  part: number
  seq: number
  isDirty: boolean
  dir: string
  session: string
}

const fileOf = (t: Trace, n: number) => `${t.dir}/${t.session}.mods.${t.load}-${n}.jsonl`

async function flush($: EngineInterface, t: Trace) {
  if (!t.isDirty || t.dir === '') return
  t.isDirty = false
  const current = t.part
  const text = `${t.lines.join('\n')}\n`
  if (t.lines.length >= PART_LINES) {
    t.part += 1
    t.lines = []
  }
  await $.fs.write(fileOf(t, current), text).catch(() => {
    t.isDirty = true
  })
}

export const register: Register = on => {
  // Modul-Zustand: ein Hot-Reload beginnt hier neu (neue <load>-Datei).
  const t: Trace = {
    load: Date.now().toString(36),
    counts: new Map(),
    lines: [],
    part: 0,
    seq: 0,
    isDirty: false,
    dir: '',
    session: 'no-session',
  }

  const record = (entry: Omit<Entry, 'ts' | 'layer' | 'seq'>) => {
    t.seq += 1
    t.counts.set(entry.event, (t.counts.get(entry.event) ?? 0) + 1)
    t.lines.push(JSON.stringify({ ts: new Date().toISOString(), layer: 'mod', seq: t.seq, ...entry } satisfies Entry))
    t.isDirty = true
  }

  on('session.start', async ($, e, next) => {
    t.session = (await $.session.id()).replace(/[^A-Za-z0-9._-]/g, '_')
    const home = (await $.env.get('HOME')) ?? '/tmp'
    t.dir = (await $.env.get('EVENT_TRACE_DIR')) ?? `${home}/.claude/event-trace`

    await $.command.register({
      name: 'event-trace',
      description: 'Zeigt, welche Hook-/Mod-Events in dieser Session gefeuert haben, und wo die Logs liegen.',
    })

    // Der Flush läuft im Timer, nicht im Hook: kein Event wartet aufs Dateisystem.
    $.clock.every(FLUSH_MS, () => {
      void flush($, t)
    })

    return next(e)
  })

  // Zum Schluss nicht auf den nächsten Timer-Tick hoffen: die Session endet.
  on('session.end', async ($, e, next) => {
    const result = await next(e)
    await flush($, t)
    return result
  })

  on('command.run', { command: 'event-trace' }, async () => {
    const top = [...t.counts.entries()].sort((a, b) => b[1] - a[1])
    const total = top.reduce((sum, [, n]) => sum + n, 0)
    const rows = top.map(([event, n]) => `  ${String(n).padStart(6)}  ${event}`).join('\n')
    return {
      text: [
        `event-trace: ${total} Mod-Events seit dem letzten Laden (${top.length} verschiedene).`,
        rows,
        '',
        `Mod-Log:   ${fileOf(t, t.part)} (Teile 0…${t.part})`,
        `Hook-Log:  ${t.dir}/${t.session}.hooks.jsonl`,
      ].join('\n'),
    }
  })

  // Der eigentliche Tracer. Auch Streaming-Events (turn.step, process.spawn)
  // kommen hier an: `next(e)` liefert dem `*`-Hook ihr Endergebnis.
  on('*', async ($, e, next) => {
    const event = String(next.event)

    // Eigene `$`-Aufrufe (fs.write des Flush, session.id, command.register) nicht
    // loggen — sonst erzeugt jeder Flush das nächste Log-Event.
    if (next.origin.plugin === 'event-trace') return next(e)

    const origin = `${next.origin.plugin}/${next.origin.tier}`
    const started = Date.now()
    try {
      const result = await next(e)
      record({
        event,
        origin,
        ms: Date.now() - started,
        outcome: isDeny(result) ? 'deny' : 'ok',
        input: clip(e),
        result: isSecretRead(event, e) ? '[redacted]' : clip(result),
      })
      return result
    } catch (error) {
      record({ event, origin, ms: Date.now() - started, outcome: 'error', input: clip(e), result: String(error) })
      throw error
    }
  })

  // `*` selektiert keine Telemetrie-Events; die werden pro Stream benannt. Nur
  // `collector` (der OpenTelemetry-Collector des Kunden): der Stream `anthropic`
  // ist den eingebauten Plugins vorbehalten — validate weist ihn ab.
  on('telemetry.*', { to: 'collector' }, async ($, e, next) => {
    const started = Date.now()
    const result = await next(e)
    record({ event: String(next.event), origin: 'telemetry/collector', ms: Date.now() - started, outcome: 'ok', input: clip(e) })
    return result
  })
}
