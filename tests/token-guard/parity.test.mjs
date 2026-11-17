// script-run: AC-tg-7-5 — copy and original agree on shared fixtures, except marked deviations.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import * as copy from '../../plugins/token-guard/hooks/lib/guard.mjs'
import { REPO } from './helpers.mjs'

const orig = await import(join(REPO, 'plugins/opencode/opencode-token-guard/dist/guard.js'))
const fx = JSON.parse(readFileSync(new URL('./fixtures/parity.json', import.meta.url), 'utf8'))

test('classifyBash parity', () => {
  for (const c of fx.classify) assert.equal(copy.classifyBash(c), orig.classifyBash(c), c)
})

test('mutatesOutsideProject parity (deviations explicit)', () => {
  for (const { cmd, deviation, expected } of fx.outside) {
    const mine = copy.mutatesOutsideProject(cmd, fx.root, fx.home)
    const theirs = orig.mutatesOutsideProject(cmd, fx.root, fx.home)
    if (deviation) {
      assert.equal(mine, expected, `copy: ${cmd}`)
      assert.notEqual(theirs, expected, `deviation no longer differs: ${cmd}`)
    } else {
      assert.equal(mine, theirs, cmd)
    }
  }
})

test('isOffloadAsk parity', () => {
  for (const t of fx.offload) assert.equal(copy.isOffloadAsk(t), orig.isOffloadAsk(t), t)
})

test('isOffloadAsk deliberate deviations (eval-driven, spec §6a)', () => {
  for (const { text, expected } of fx.offloadDeviations) {
    assert.equal(copy.isOffloadAsk(text), expected, `copy: ${text}`)
    assert.notEqual(orig.isOffloadAsk(text), expected, `deviation no longer differs: ${text}`)
  }
})
