// plugin-guard — der Mod-Teil: ein Gate vor jedem Hooks-Modul (JS/TS).
//
// `plugin.register` feuert für jedes Hooks-Modul, das der Kette beitreten will —
// beim Start und bei jedem Reload (Update, /reload-plugins, Hot-Reload). Der Hook
// liest den Quellcode des Plugins, prüft ihn gegen rules/rules.json, bewertet die
// Fähigkeiten, die die Engine aus dem Modul gelesen hat (`e.uses`), und bildet
// einen SHA-256 über den Code. Ab `blockAt` wird das Modul abgelehnt — bis die
// Person genau diesen Stand mit `/plugin-guard approve <name>` freigibt. Ändert
// ein Update den Code, ändert sich der Hash und die Freigabe gilt nicht mehr.
//
// Grenze: Der Wächter urteilt nur über Module, die NACH ihm zugelassen werden
// (gleicher Tier: Reihenfolge der Plugins). Vollständig wird das Gate als
// Managed-Plugin (Tier `prepend`) — siehe README.

import type { EngineInterface, PluginRegisterInput, PluginRegisterUses, Register } from 'claude-code'

type Severity = 'low' | 'medium' | 'high' | 'critical'
type Level = Severity | 'none'

type SourceRule = { id: string; severity: Severity; pattern: string; flags?: string; why: string }
type MatchRule = { match: string; severity: Severity; why: string }
type Rules = {
  codeExtensions: string[]
  skipPaths: string[]
  skipFiles: string[]
  maxFiles: number
  maxFileBytes: number
  sourceRules: SourceRule[]
  capabilityRules: {
    calls: MatchRule[]
    events: MatchRule[]
    sensitiveEnv: { severity: Severity; pattern: string; why: string }
    dangerousEnvWrites: { severity: Severity; pattern: string; why: string }
    combos: { all: string[]; severity: Severity; why: string }[]
  }
}

type Finding = { rule: string; severity: Severity; why: string; where?: string }

type Verdict = {
  name: string
  provenance: string
  root: string
  version?: string
  hash: string
  level: Level
  decision: 'admitted' | 'approved' | 'refused' | 'skipped'
  changed: boolean
  findings: Finding[]
  at: string
}

const RANK: Record<Level, number> = { none: 0, low: 1, medium: 2, high: 3, critical: 4 }
const VERDICTS = 'verdicts'
const APPROVED = 'approved'
const SEEN = 'seen'

const maxLevel = (findings: Finding[]): Level =>
  findings.reduce<Level>((top, f) => (RANK[f.severity] > RANK[top] ? f.severity : top), 'none')

const asRecord = (value: unknown): Record<string, string> =>
  typeof value === 'object' && value !== null ? (value as Record<string, string>) : {}

async function sha256(text: string): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('')
}

async function loadRules($: EngineInterface): Promise<Rules> {
  return JSON.parse(await $.fs.read(`${$.plugin.root}/rules/rules.json`)) as Rules
}

// Alle Code-Dateien unter `root`, relativ, sortiert. Zu große Dateien und das
// Überschreiten von maxFiles werden selbst zum Befund: ungeprüfter Code ist ein Risiko.
async function listCode($: EngineInterface, root: string, rules: Rules, findings: Finding[]): Promise<string[]> {
  const files: string[] = []
  const queue = ['']
  while (queue.length > 0) {
    const rel = queue.shift() as string
    const entries = await $.fs.list(rel === '' ? root : `${root}/${rel}`).catch(() => [])
    for (const entry of entries) {
      const path = rel === '' ? entry.name : `${rel}/${entry.name}`
      if (entry.kind === 'dir') {
        if (!rules.skipPaths.includes(path)) queue.push(path)
        continue
      }
      if (entry.isLink) {
        findings.push({ rule: 'symlink', severity: 'medium', why: 'Link — Ziel liegt evtl. außerhalb des Plugins', where: path })
        continue
      }
      if (rel === '' && rules.skipFiles.includes(entry.name)) continue
      if (entry.kind !== 'file' || !rules.codeExtensions.some(ext => entry.name.endsWith(ext))) continue
      if (entry.size > rules.maxFileBytes) {
        findings.push({ rule: 'unscanned-large-file', severity: 'medium', why: 'zu groß zum Prüfen', where: path })
        continue
      }
      if (files.length >= rules.maxFiles) {
        findings.push({ rule: 'too-many-files', severity: 'medium', why: `mehr als ${rules.maxFiles} Code-Dateien — Rest ungeprüft` })
        return files.sort()
      }
      files.push(path)
    }
  }
  return files.sort()
}

// Quellcode gegen die Regeln; liefert zugleich den Hash über genau diesen Code.
async function scanSource($: EngineInterface, root: string, rules: Rules, findings: Finding[]): Promise<string> {
  const files = await listCode($, root, rules, findings)
  const compiled = rules.sourceRules.map(rule => ({ rule, re: new RegExp(rule.pattern, `g${rule.flags ?? ''}`) }))
  let material = ''
  for (const file of files) {
    const text = await $.fs.read(`${root}/${file}`).catch(() => '')
    material += `${file}\u0000${text}\u0000`
    for (const { rule, re } of compiled) {
      re.lastIndex = 0
      const match = re.exec(text)
      if (match === null) continue
      const line = text.slice(0, match.index).split('\n').length
      findings.push({ rule: rule.id, severity: rule.severity, why: rule.why, where: `${file}:${line}` })
    }
  }
  return sha256(material)
}

// Was die Engine aus dem Modul gelesen hat — exakt, weil ein Modul `$`, `on` und
// `$.env` nur literal schreiben darf.
function judgeUses(uses: PluginRegisterUses, rules: Rules, findings: Finding[]) {
  const cap = rules.capabilityRules
  for (const rule of cap.calls) {
    if (uses.calls.includes(rule.match)) findings.push({ rule: `call:${rule.match}`, severity: rule.severity, why: rule.why })
  }
  for (const rule of cap.events) {
    if (uses.events.includes(rule.match)) findings.push({ rule: `event:${rule.match}`, severity: rule.severity, why: rule.why })
  }
  const secretReads = (uses.env?.reads ?? []).filter(name => new RegExp(cap.sensitiveEnv.pattern).test(name))
  if (secretReads.length > 0) {
    findings.push({ rule: 'env:secret-read', severity: cap.sensitiveEnv.severity, why: cap.sensitiveEnv.why, where: secretReads.join(', ') })
  }
  const writes = (uses.env?.writes ?? []).filter(name => new RegExp(cap.dangerousEnvWrites.pattern).test(name))
  if (writes.length > 0) {
    findings.push({ rule: 'env:dangerous-write', severity: cap.dangerousEnvWrites.severity, why: cap.dangerousEnvWrites.why, where: writes.join(', ') })
  }
  const traits = new Set([...uses.calls, ...(secretReads.length > 0 ? ['secret-env'] : [])])
  for (const combo of cap.combos) {
    if (combo.all.every(trait => traits.has(trait))) {
      findings.push({ rule: `combo:${combo.all.join('+')}`, severity: combo.severity, why: combo.why })
    }
  }
}

async function judge($: EngineInterface, e: PluginRegisterInput, blockAt: string): Promise<Verdict> {
  const rules = await loadRules($)
  const findings: Finding[] = []
  const hash = await scanSource($, e.root, rules, findings)
  judgeUses(e.uses, rules, findings)
  findings.sort((a, b) => RANK[b.severity] - RANK[a.severity])

  const approved = asRecord(await $.store.get(APPROVED))
  const seen = asRecord(await $.store.get(SEEN))
  const level = maxLevel(findings)
  const changed = seen[e.root] !== undefined && seen[e.root] !== hash
  await $.store.set(SEEN, { ...seen, [e.root]: hash })

  const isApproved = approved[e.root] === hash
  const blocks = blockAt !== 'off' && RANK[level] >= RANK[blockAt as Level]
  const decision = isApproved ? 'approved' : blocks ? 'refused' : 'admitted'

  return {
    name: e.name,
    provenance: e.provenance,
    root: e.root,
    version: e.version,
    hash,
    level,
    decision,
    changed,
    findings,
    at: new Date().toISOString(),
  }
}

async function remember($: EngineInterface, verdict: Verdict) {
  const all = (await $.store.get(VERDICTS)) as Record<string, Verdict> | undefined
  await $.store.set(VERDICTS, { ...(all ?? {}), [verdict.root]: verdict })
}

const summary = (v: Verdict) =>
  v.findings
    .filter(f => RANK[f.severity] >= RANK.medium)
    .slice(0, 3)
    .map(f => `${f.severity} ${f.rule}${f.where ? ` (${f.where})` : ''}`)
    .join('; ')

function report(verdicts: Verdict[], approved: Record<string, string>, current: Set<string>): string {
  if (verdicts.length === 0) return 'plugin-guard: noch kein Hooks-Modul geprüft (nur Module, die nach plugin-guard laden, kommen hier an).'
  const lines = verdicts
    .sort((a, b) => RANK[b.level] - RANK[a.level])
    .map(v => {
      const head = `${v.decision.toUpperCase().padEnd(8)} ${v.name}@${v.version ?? '?'}  [${v.level}]${v.changed ? '  ⟳ geändert seit letzter Prüfung' : ''}${approved[v.root] === v.hash ? '  ✔ freigegeben' : ''}${current.has(v.root) ? '' : `  (frühere Sitzung, ${v.at.slice(0, 16)})`}`
      const details = v.findings
        .filter(f => RANK[f.severity] >= RANK.medium)
        .map(f => `           - ${f.severity.padEnd(8)} ${f.rule}: ${f.why}${f.where ? ` — ${f.where}` : ''}`)
      return [head, `           ${v.provenance} · ${v.root} · sha256 ${v.hash.slice(0, 12)}…`, ...details].join('\n')
    })
  return ['plugin-guard — Urteile über Hooks-Module (JS/TS):', '', ...lines, '', 'Freigeben: /plugin-guard approve <name>, danach /reload-plugins · Zurückziehen: /plugin-guard revoke <name>'].join('\n')
}

// Meldungen an die Person; scheitern sie (z. B. noch keine Oberfläche), bleibt das
// Urteil davon unberührt.
function say($: EngineInterface, text: string, toast?: string) {
  try {
    $.ui.log(text)
    if (toast !== undefined) $.ui.toast(toast)
  } catch {
    // keine Oberfläche — das Urteil steht trotzdem
  }
}

export const register: Register = (on, options) => {
  const blockAt = String(options.blockAt ?? 'high')
  // Urteile DIESER Ladung; im Store liegen auch die früherer Sitzungen.
  const current = new Set<string>()

  on('plugin.register', async ($, e, next) => {
    // Eingebaute und vom Admin verwaltete Plugins sind nicht unsere Entscheidung.
    if (e.tier !== 'user') return next(e)

    const verdict = await judge($, e, blockAt)
    await remember($, verdict)
    current.add(verdict.root)

    if (verdict.decision === 'refused') {
      const reason = `plugin-guard: ${e.name} blockiert [${verdict.level}] — ${summary(verdict)}. Prüfen: /plugin-guard · freigeben: /plugin-guard approve ${e.name}`
      say($, reason, `plugin-guard hat ${e.name} blockiert (${verdict.level}) — /plugin-guard`)
      return { refuse: reason }
    }
    if (RANK[verdict.level] >= RANK.medium && verdict.decision !== 'approved') {
      say($, `plugin-guard: ${e.name} geladen mit Befunden [${verdict.level}] — ${summary(verdict)}`)
    }
    return next(e)
  }).catch(($, e, next) =>
    // Ein Gate, das selbst scheitert, lässt nichts Ungeprüftes durch.
    next.called ? next(e) : { refuse: `plugin-guard: Prüfung von ${e.name} fehlgeschlagen (${next.error.kind}) — sicherheitshalber blockiert` },
  )

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'plugin-guard',
      description: 'Zeigt die Sicherheitsurteile über Plugin-Hooks-Module; approve/revoke <plugin> gibt einen geprüften Stand frei.',
      argumentHint: '[approve|revoke <plugin>]',
    })
    const verdicts = Object.values(((await $.store.get(VERDICTS)) ?? {}) as Record<string, Verdict>)
    const refused = verdicts.filter(v => v.decision === 'refused' && current.has(v.root))
    if (refused.length > 0) {
      const names = refused.map(v => v.name).join(', ')
      say($, `plugin-guard: blockiert: ${names}`, `plugin-guard: ${refused.length} Plugin-Modul(e) blockiert: ${names} — /plugin-guard`)
    }
    return next(e)
  })

  on('command.run', { command: 'plugin-guard' }, async ($, e) => {
    const verdicts = Object.values(((await $.store.get(VERDICTS)) ?? {}) as Record<string, Verdict>)
    const approved = asRecord(await $.store.get(APPROVED))
    const [action, name] = e.args.trim().split(/\s+/)

    if (action === 'approve' || action === 'revoke') {
      // Freigaben nur von der Person selbst — nicht vom Modell, einem Plugin oder
      // einer eingespielten Nachricht (Prompt-Injection).
      if (e.origin.kind !== 'composer' && e.origin.kind !== 'bridge') {
        return { text: `plugin-guard: ${action} nur per eigener Eingabe der Person (Herkunft war: ${e.origin.kind}).` }
      }
      const target = verdicts.find(v => v.name === name)
      if (target === undefined) return { text: `plugin-guard: kein geprüftes Plugin namens "${name ?? ''}".` }
      if (action === 'approve') {
        await $.store.set(APPROVED, { ...approved, [target.root]: target.hash })
        return { text: `plugin-guard: ${target.name} in genau diesem Stand freigegeben (sha256 ${target.hash.slice(0, 12)}…). Laden mit /reload-plugins. Ein Update ändert den Hash und braucht eine neue Freigabe.` }
      }
      const { [target.root]: _gone, ...rest } = approved
      await $.store.set(APPROVED, rest)
      return { text: `plugin-guard: Freigabe für ${target.name} zurückgezogen — wirkt beim nächsten Laden/Reload.` }
    }

    return { text: report(verdicts, approved, current) }
  })
}
