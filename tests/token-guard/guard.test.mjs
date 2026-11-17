// script-run: pure logic of hooks/lib/guard.mjs (AC-tg-1-1, 1-3, 2-3, 4-1, 7-1).
import { test } from 'node:test'
import assert from 'node:assert/strict'
import * as g from '../../plugins/token-guard/hooks/lib/guard.mjs'

test('AC-tg-1-1 classifyBash', () => {
  assert.equal(g.classifyBash('npm test'), 'verify')
  assert.equal(g.classifyBash('npx tsc --noEmit'), 'verify')
  assert.equal(g.classifyBash('ls && pwd'), 'chained')
  assert.equal(g.classifyBash('for f in *; do echo $f; done'), 'chained')
  assert.equal(g.classifyBash('ls -la'), 'single')
})

test('AC-tg-1-3 streak resets on chained/verify and after a block', () => {
  const s = g.freshState()
  const o = { ...g.DEFAULTS, maxConsecutiveBash: 2 }
  assert.ok(g.onBashBefore(s, o, 'ls').allow)
  assert.ok(g.onBashBefore(s, o, 'pwd').allow)
  assert.equal(g.onBashBefore(s, o, 'whoami').allow, false)
  assert.ok(g.onBashBefore(s, o, 'ls').allow) // fresh after block
  assert.ok(g.onBashBefore(s, o, 'a && b').allow)
  assert.equal(s.consecutiveSingleBash, 0)
})

test('AC-tg-2-3 verify in PreToolUse keeps edit count; PostToolUse resets it', () => {
  const s = g.freshState()
  const o = g.DEFAULTS
  g.onEdit(s)
  g.onBashBefore(s, o, 'npm test')
  assert.equal(s.editsSinceVerify, 1)
  assert.match(g.onVerifyAfter(s, o), /after only 1 edit/)
  assert.equal(s.editsSinceVerify, 0)
  assert.equal(g.onVerifyAfter(s, o), null) // 0 edits → no nudge
})

test('AC-tg-4-1 outside-project detection incl. allowlist directories themselves', () => {
  const root = '/Users/x/proj', home = '/Users/x'
  const out = (c) => g.mutatesOutsideProject(c, root, home)
  assert.ok(out('echo hi > /etc/foo'))
  assert.ok(out('touch ~/notes.txt'))
  assert.ok(out('cd /Users/x/other && cp a b'))
  assert.ok(out('sed -i s/a/b/ /Users/x/other/f'))
  assert.equal(out('cat /etc/hosts'), false)
  assert.equal(out('echo hi > ./local.txt'), false)
  assert.equal(out('touch /Users/x/proj/sub/f'), false)
  assert.equal(out('echo x > /tmp/f'), false)
  assert.equal(out('cd /tmp && touch x'), false) // DEVIATION vs opencode
  assert.equal(out('cd /private/tmp && touch x'), false)
  assert.equal(out('echo x > /dev/null'), false)
  assert.equal(out('cat client/src/foo.ts > out.txt'), false)
})

test('AC-tg-7-1 env parsing: integers only, 0 = off', () => {
  assert.deepEqual(g.optionsFromEnv({}), g.DEFAULTS)
  for (const bad of ['', 'abc', '8abc', '2.5', '-3', '1e3']) {
    assert.equal(g.optionsFromEnv({ TOKEN_GUARD_MAX_CONSECUTIVE_BASH: bad }).maxConsecutiveBash, 8, bad)
  }
  const o = g.optionsFromEnv({
    TOKEN_GUARD_MAX_CONSECUTIVE_BASH: '0', TOKEN_GUARD_MIN_EDITS_PER_VERIFY: '0',
    TOKEN_GUARD_STEP_BUDGET: '0', TOKEN_GUARD_CONTEXT_BUDGET: '0',
  })
  const s = g.freshState()
  for (let i = 0; i < 50; i++) assert.ok(g.onBashBefore(s, o, 'ls').allow)
  g.onEdit(s)
  assert.equal(g.onVerifyAfter(s, o), null)
  s.steps = 10_000
  s.lastContextTokens = 10_000_000
  assert.equal(g.checkStepBudget(s, o), null)
  assert.equal(g.checkContextBudget(s, o), null)
})

test('AC-tg-3-3 budgets nudge once', () => {
  const s = g.freshState()
  const o = { ...g.DEFAULTS, stepBudget: 2, contextBudgetTokens: 100 }
  s.steps = 3
  s.lastContextTokens = 200
  assert.ok(g.checkStepBudget(s, o))
  assert.equal(g.checkStepBudget(s, o), null)
  assert.ok(g.checkContextBudget(s, o))
  assert.equal(g.checkContextBudget(s, o), null)
})
