// script-run: metrics, stats report, transcript reader, perf (AC-tg-3-1, 3-2, 3-5, 6-1..6-3, 7-4).
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { spawn, spawnSync } from 'node:child_process'
import { appendFileSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { bumpMetrics, readMetrics } from '../../plugins/token-guard/hooks/lib/store.mjs'
import { advanceTranscript } from '../../plugins/token-guard/hooks/lib/transcript.mjs'
import { freshState } from '../../plugins/token-guard/hooks/lib/guard.mjs'
import { PLUGIN, sandbox } from './helpers.mjs'

const tmp = () => mkdtempSync(join(tmpdir(), 'tg-'))

test('AC-tg-6-1 metrics schema and counters', () => {
  const env = { TOKEN_GUARD_METRICS_PATH: join(tmp(), 'm.json') }
  bumpMetrics('verifyChurn', 's1', true, env)
  bumpMetrics('verifyChurn', 's1', false, env)
  bumpMetrics('offloadAsk', 's2', true, env)
  const m = readMetrics(env)
  assert.equal(m.verifyChurn, 2); assert.equal(m.offloadAsk, 1)
  assert.equal(m.total, 3); assert.equal(m.sessions, 2)
  assert.ok(m.firstFiring && m.lastFiring)
  for (const k of ['stepBudget', 'contextBudget', 'blockedBashStreaks', 'blockedOutsideMutation', 'lastSessionId']) {
    assert.ok(k in m, k)
  }
})

test('AC-tg-6-2 parallel writers lose no count', async () => {
  const path = join(tmp(), 'm.json')
  const script = `import('${PLUGIN}/hooks/lib/store.mjs').then(s => { for (let i = 0; i < 10; i++) s.bumpMetrics('stepBudget', 'x', false) })`
  await Promise.all(Array.from({ length: 8 }, () => new Promise((res, rej) => {
    const p = spawn(process.execPath, ['-e', script], { env: { ...process.env, TOKEN_GUARD_METRICS_PATH: path } })
    p.on('exit', (c) => (c === 0 ? res() : rej(new Error('exit ' + c))))
  })))
  assert.equal(readMetrics({ TOKEN_GUARD_METRICS_PATH: path }).stepBudget, 80)
})

test('AC-tg-6-3 stats script is deterministic', () => {
  const dir = tmp()
  const path = join(dir, 'm.json')
  const env = { ...process.env, TOKEN_GUARD_METRICS_PATH: path }
  const run = () => spawnSync(process.execPath, [join(PLUGIN, 'hooks/stats.mjs')], { env, encoding: 'utf8' }).stdout
  assert.match(run(), /No firings recorded yet/)
  writeFileSync(path, JSON.stringify({ blockedBashStreaks: 5, total: 5, sessions: 2, firstFiring: 'a', lastFiring: 'b' }))
  const a = run()
  assert.equal(a, run())
  assert.match(a, /blocked Bash streaks\s+5/)
  assert.match(a, /ESTIMATE \(heuristic, not measured\): ~20 provider steps/)
})

test('AC-tg-3-1 / 3-2 / 3-5 transcript: steps per message id, context sum, incremental', () => {
  const p = join(tmp(), 't.jsonl')
  const line = (o) => JSON.stringify(o) + '\n'
  writeFileSync(p,
    line({ type: 'user', message: { role: 'user', content: 'hi' } }) +
    line({ type: 'assistant', message: { id: 'a', content: [{ type: 'text', text: 'x' }], usage: { input_tokens: 1 } } }) +
    line({ type: 'assistant', message: { id: 'a', content: [{ type: 'tool_use' }], usage: { input_tokens: 2, cache_read_input_tokens: 30, cache_creation_input_tokens: 400 } } }) +
    line({ type: 'assistant', isSidechain: true, message: { id: 'sub', usage: { input_tokens: 99999 } } }))
  const s = freshState()
  advanceTranscript(s, p)
  assert.equal(s.steps, 1)
  assert.equal(s.lastContextTokens, 432)
  const off = s.transcriptOffset
  appendFileSync(p, '{"type":"assistant","message":{"id":"b"') // partial line
  advanceTranscript(s, p)
  assert.equal(s.transcriptOffset, off)
  appendFileSync(p, ',"content":[{"type":"text","text":"bye"}]}}\n')
  advanceTranscript(s, p)
  assert.equal(s.steps, 2)
  assert.equal(s.lastAssistantText, 'bye')
})

test('AC-tg-7-4 median hook latency < 200 ms on a 2 000-line transcript', () => {
  const sb = sandbox()
  for (let i = 0; i < 2000; i++) sb.assistant('m' + i)
  const times = []
  for (let i = 0; i < 20; i++) {
    const t = performance.now()
    sb.run('PostToolUse', { tool_name: 'Read', tool_input: {} })
    times.push(performance.now() - t)
  }
  times.sort((a, b) => a - b)
  const median = times[10]
  assert.ok(median < 200, `median ${median.toFixed(0)} ms`)
})
