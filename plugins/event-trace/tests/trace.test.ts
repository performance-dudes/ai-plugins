// `claude plugin test plugins/event-trace` — der Mod gegen die echte Engine.
// Die Hooks des Tests sitzen UNTER dem Plugin und spielen die Welt: Session-Id,
// Dateisystem (fängt $.fs.write ab), Uhr und Umgebung (mock).
import { expect, mock, test } from 'claude-code/testing'

const START = { cwd: '/work', surface: 'terminal', isInteractive: true } as const

test('loggt jedes Event als JSONL, reicht unverändert durch und fasst per /event-trace zusammen', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/home/tester' })
  const writes = new Map<string, string>()

  on('session.id', async () => ({ value: 'sess-1' }))
  on('command.register', async ($, e) => ({ value: { command: e.name } }))
  on('session.start', async ($, e) => ({ cwd: e.cwd }))
  on('fs.write', async ($, e) => {
    writes.set(e.path, e.text)
    return { value: undefined }
  })
  on('classic.Stop', async () => ({}))

  await $.session.start(START)
  // ein klassisches Event, wie es der Settings-Hook-Pfad auslöst
  const stop = await $.classic.Stop({ stop_hook_active: false } as never)
  expect(stop).toEqual({})

  await clock.advance(1100)

  const files = [...writes.keys()]
  expect(files.length).toBe(1)
  const [file] = files
  expect(file).toMatch(/^\/home\/tester\/\.claude\/event-trace\/sess-1\.mods\.[a-z0-9]+-0\.jsonl$/)

  const entries = (writes.get(file!) ?? '').trim().split('\n').map(line => JSON.parse(line))
  const events = entries.map(entry => entry.event)
  expect(events).toContain('session.start')
  expect(events).toContain('classic.Stop')
  // eigene $-Aufrufe (fs.write, session.id, command.register) werden nicht geloggt
  expect(events).not.toContain('fs.write')
  expect(events).not.toContain('session.id')
  for (const entry of entries) {
    expect(entry.layer).toBe('mod')
    expect(entry.outcome).toBe('ok')
  }

  const summary = await $.command.run({
    command: 'event-trace',
    args: '',
    origin: { kind: 'composer' },
    presentation: { isFullscreen: false, columns: 120 },
  } as never)
  const text = (summary as { text: string }).text
  expect(text).toMatch(/classic\.Stop/)
  expect(text).toMatch(/sess-1\.hooks\.jsonl/)
})

test('EVENT_TRACE_DIR legt das Log-Verzeichnis fest', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/home/tester', EVENT_TRACE_DIR: '/var/trace' })
  const paths: string[] = []

  on('session.id', async () => ({ value: 'sess-2' }))
  on('command.register', async ($, e) => ({ value: { command: e.name } }))
  on('session.start', async ($, e) => ({ cwd: e.cwd }))
  on('fs.write', async ($, e) => {
    paths.push(e.path)
    return { value: undefined }
  })

  await $.session.start(START)
  await clock.advance(1100)

  expect(paths.length).toBeGreaterThan(0)
  expect(paths[0]).toMatch(/^\/var\/trace\/sess-2\.mods\./)
})

test('maskiert Werte unter sensiblen Schlüsseln (Token, Authorization, API-Key)', async ($, on) => {
  const clock = mock.clock(on)
  mock.env(on, { HOME: '/home/tester' })
  let log = ''

  on('session.id', async () => ({ value: 'sess-3' }))
  on('command.register', async ($, e) => ({ value: { command: e.name } }))
  on('session.start', async ($, e) => ({ cwd: e.cwd }))
  on('fs.write', async ($, e) => {
    log = e.text
    return { value: undefined }
  })
  on('classic.Notification', async () => ({}))

  await $.session.start(START)
  await $.classic.Notification({
    message: 'sichtbar',
    notification_type: 'idle_prompt',
    headers: { Authorization: 'Bearer sk-geheim-123', 'x-api-key': 'sk-geheim-456' },
  } as never)
  await clock.advance(1100)

  expect(log).toMatch(/"event":"classic\.Notification"/)
  expect(log).toMatch(/sichtbar/)
  expect(log).toMatch(/\[redacted\]/)
  expect(log).not.toMatch(/sk-geheim/)
})
