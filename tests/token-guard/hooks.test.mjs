// hook-behavior: the real hooks.json command per event (US-tg-1..5, AC-tg-7-2, 7-3).
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname } from 'node:path'
import { sandbox, denied, ctx } from './helpers.mjs'

test('AC-tg-1-2 / 1-4 / 1-5 streak block via PreToolUse, persisted per session', () => {
  const sb = sandbox({ TOKEN_GUARD_MAX_CONSECUTIVE_BASH: '2' })
  assert.equal(denied(sb.bash('ls')), false)
  sb.run('PreToolUse', { tool_name: 'Read', tool_input: { file_path: 'x' } }) // non-Bash: no effect
  assert.equal(denied(sb.bash('pwd')), false)
  const r = sb.bash('whoami')
  assert.ok(denied(r))
  assert.match(r.json.hookSpecificOutput.permissionDecisionReason, /3 consecutive single-purpose Bash calls/)
  assert.equal(sb.metrics().blockedBashStreaks, 1)
  const first = sb.sid
  sb.sid = 'other-session'
  assert.equal(denied(sb.bash('ls')), false) // separate counter
  sb.sid = first
})

test('AC-tg-4-2 / 4-3 outside mutation denied before rationing', () => {
  const sb = sandbox({ TOKEN_GUARD_MAX_CONSECUTIVE_BASH: '1' })
  sb.bash('ls')
  const r = sb.bash(`touch /srv/tg/elsewhere.txt`) // also the 2nd single call
  assert.ok(denied(r))
  assert.match(r.json.hookSpecificOutput.permissionDecisionReason, /outside the project root/)
  assert.ok(r.json.hookSpecificOutput.permissionDecisionReason.includes(sb.project))
  assert.equal(denied(sb.bash(`touch ${sb.project}/inside.txt && ls`)), false)
  // fallback to cwd when CLAUDE_PROJECT_DIR is unset
  const r2 = sb.run('PreToolUse', { tool_name: 'Bash', tool_input: { command: `touch /srv/tg/x` } },
    { env: { CLAUDE_PROJECT_DIR: '' } })
  assert.ok(denied(r2))
})

test('AC-tg-2-1 / 2-2 verify churn goes to the model via PostToolUse', () => {
  const sb = sandbox()
  sb.run('PreToolUse', { tool_name: 'Edit', tool_input: {} })
  sb.bash('npm test')
  const r = sb.run('PostToolUse', { tool_name: 'Bash', tool_input: { command: 'npm test' } })
  assert.match(ctx(r), /verification ran after only 1 edit/)
  for (let i = 0; i < 3; i++) sb.run('PreToolUse', { tool_name: 'Write', tool_input: {} })
  const r2 = sb.run('PostToolUse', { tool_name: 'Bash', tool_input: { command: 'npm test' } })
  assert.equal(ctx(r2), '')
  assert.equal(sb.metrics().verifyChurn, 1)
})

test('AC-tg-3-3 / 3-4 budgets: PostToolUse → model; Stop → user now, model next prompt', () => {
  const sb = sandbox({ TOKEN_GUARD_STEP_BUDGET: '2', TOKEN_GUARD_CONTEXT_BUDGET: '1000' })
  sb.assistant('m1')
  sb.assistant('m1') // same message id → one step
  sb.assistant('m2')
  assert.equal(ctx(sb.run('PostToolUse', { tool_name: 'Read', tool_input: {} })), '')
  sb.assistant('m3', { usage: { input_tokens: 5, cache_read_input_tokens: 2000, cache_creation_input_tokens: 0 } })
  const r = sb.run('PostToolUse', { tool_name: 'Read', tool_input: {} })
  assert.match(ctx(r), /3 provider steps/)
  assert.match(ctx(r), /context is at 2k tokens/)
  sb.assistant('m4', { text: 'done' })
  assert.equal(sb.run('Stop', {}).json, null) // already nudged once

  const sb2 = sandbox({ TOKEN_GUARD_STEP_BUDGET: '1' })
  sb2.assistant('a', { text: 'x' })
  sb2.assistant('b', { text: 'all done' })
  const s = sb2.run('Stop', {})
  assert.match(s.json.systemMessage, /2 provider steps/)
  const u = sb2.run('UserPromptSubmit', { prompt: 'next' })
  assert.match(ctx(u), /2 provider steps/)
  assert.equal(ctx(sb2.run('UserPromptSubmit', { prompt: 'again' })), '') // delivered once
})

test('AC-tg-5-1 / 5-2 offload ask detected at Stop, never blocks', () => {
  const sb = sandbox()
  sb.assistant('m1', { text: 'Please run this yourself in your terminal: npm i' })
  const s = sb.run('Stop', {})
  assert.equal(s.code, 0)
  assert.equal(s.json.decision, undefined)
  assert.match(s.json.systemMessage, /asked the user to run/)
  assert.match(ctx(sb.run('UserPromptSubmit', { prompt: 'ok' })), /asked the user to run/)
  assert.equal(sb.run('Stop', {}).json, null) // same message not re-flagged
  assert.equal(sb.metrics().offloadAsk, 1)
  // last_assistant_message from the hook input wins over the transcript
  const sb2 = sandbox()
  const s2 = sb2.run('Stop', { last_assistant_message: 'Führe das bitte selbst aus.' })
  assert.match(s2.json.systemMessage, /asked the user/)
})

test('AC-tg-7-2 fail-open on bad input, bad session id, corrupt state, missing node', () => {
  const sb = sandbox({ TOKEN_GUARD_MAX_CONSECUTIVE_BASH: '0' })
  for (const raw of ['', 'not json', '{}', '[]']) {
    const r = sb.run('PreToolUse', {}, { raw })
    assert.equal(r.code, 0); assert.equal(r.stdout, '')
  }
  sb.sid = '../../etc/passwd'
  assert.equal(sb.bash('touch /etc/x').stdout, '')
  sb.sid = 'corrupt'
  mkdirSync(dirname(sb.statePath()), { recursive: true })
  writeFileSync(sb.statePath(), '{broken')
  const r = sb.bash(`touch /srv/tg/x`)
  assert.ok(denied(r)) // corrupt state replaced by a fresh one, guard still works
  const noNode = sb.run('PreToolUse', { tool_name: 'Bash', tool_input: { command: `touch /srv/tg/x` } },
    { env: { PATH: '/nonexistent' } })
  assert.equal(noNode.code, 0); assert.equal(noNode.stdout, '')
  const missing = sb.run('PostToolUse', { tool_name: 'Read', transcript_path: '/nonexistent.jsonl' })
  assert.equal(missing.code, 0)
})

test('AC-tg-7-3 state file per session, deleted on SessionEnd', () => {
  const sb = sandbox()
  sb.bash('ls')
  assert.ok(existsSync(sb.statePath()))
  sb.run('SessionEnd', { reason: 'exit' })
  assert.equal(existsSync(sb.statePath()), false)
})
