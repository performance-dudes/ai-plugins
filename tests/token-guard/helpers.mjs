// Shared helpers: run the REAL hook command from hooks.json (object under test,
// not a copy) in an isolated HOME.

import { spawnSync } from 'node:child_process'
import { mkdtempSync, readFileSync, writeFileSync, appendFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
export const REPO = resolve(here, '../..')
export const PLUGIN = join(REPO, 'plugins/token-guard')
export const HOOKS_JSON = JSON.parse(readFileSync(join(PLUGIN, 'hooks/hooks.json'), 'utf8'))

export function hookCommand(event) {
  return HOOKS_JSON.hooks[event][0].hooks[0].command
}

export function sandbox(extraEnv = {}) {
  const home = mkdtempSync(join(tmpdir(), 'tg-home-'))
  const project = mkdtempSync(join(home, 'proj-'))
  const transcript = join(home, 'transcript.jsonl')
  writeFileSync(transcript, '')
  const env = {
    PATH: process.env.PATH,
    HOME: home,
    CLAUDE_PLUGIN_ROOT: PLUGIN,
    CLAUDE_PROJECT_DIR: project,
    ...extraEnv,
  }
  let sid = 'sess-' + Math.random().toString(36).slice(2, 10)
  const run = (event, payload = {}, opts = {}) => {
    const input = {
      session_id: sid, transcript_path: transcript, cwd: project, hook_event_name: event, ...payload,
    }
    const r = spawnSync('/bin/sh', ['-c', hookCommand(event)], {
      input: typeof opts.raw === 'string' ? opts.raw : JSON.stringify(input),
      env: { ...env, ...(opts.env ?? {}) },
      encoding: 'utf8',
    })
    let json = null
    if (r.stdout.trim()) json = JSON.parse(r.stdout)
    return { code: r.status, stdout: r.stdout, stderr: r.stderr, json }
  }
  const bash = (command) => run('PreToolUse', { tool_name: 'Bash', tool_input: { command } })
  const assistant = (id, { text, usage } = {}) =>
    appendFileSync(
      transcript,
      JSON.stringify({
        type: 'assistant',
        message: {
          id, role: 'assistant',
          content: text ? [{ type: 'text', text }] : [{ type: 'tool_use', id: 't', name: 'Bash', input: {} }],
          usage: usage ?? { input_tokens: 10, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 },
        },
      }) + '\n',
    )
  return {
    home, project, transcript, env, run, bash, assistant,
    get sid() { return sid },
    set sid(v) { sid = v },
    metrics: () => JSON.parse(readFileSync(join(home, '.claude/token-guard-metrics.json'), 'utf8')),
    statePath: () => join(home, '.claude/token-guard/sessions', `${sid}.json`),
  }
}

export const denied = (r) => r.json?.hookSpecificOutput?.permissionDecision === 'deny'
export const ctx = (r) => r.json?.hookSpecificOutput?.additionalContext ?? ''
