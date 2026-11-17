// File-backed state for token-guard: per-session guard state and the global
// firing metrics. Every hook event is its own process, and parallel tool calls
// run hooks concurrently, so both files are read-modify-written under a lock
// directory and replaced atomically (write temp file, then rename).

import {
  mkdirSync, readFileSync, renameSync, rmSync, rmdirSync, statSync, writeFileSync,
} from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { freshState } from './guard.mjs'

const LOCK_WAIT_MS = 400
const LOCK_STALE_MS = 3000
const SESSION_ID_RE = /^[A-Za-z0-9_-]+$/

const home = (env) => env.HOME || homedir()

export const stateDir = (env = process.env) => join(home(env), '.claude', 'token-guard', 'sessions')

export function metricsPath(env = process.env) {
  return env.TOKEN_GUARD_METRICS_PATH || join(home(env), '.claude', 'token-guard-metrics.json')
}

export function validSessionId(id) {
  return typeof id === 'string' && SESSION_ID_RE.test(id)
}

const sleep = (ms) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms)

/** Runs fn while holding `<path>.lock`. Throws when the lock can't be taken. */
export function withLock(path, fn) {
  const lock = path + '.lock'
  mkdirSync(dirname(path), { recursive: true })
  const deadline = Date.now() + LOCK_WAIT_MS
  for (;;) {
    try {
      mkdirSync(lock)
      break
    } catch (e) {
      if (e.code !== 'EEXIST') throw e
      try {
        if (Date.now() - statSync(lock).mtimeMs > LOCK_STALE_MS) rmdirSync(lock)
      } catch {}
      if (Date.now() > deadline) throw new Error('token-guard: lock timeout')
      sleep(5)
    }
  }
  try {
    return fn()
  } finally {
    try { rmdirSync(lock) } catch {}
  }
}

function writeAtomic(path, value) {
  const tmp = `${path}.${process.pid}.tmp`
  writeFileSync(tmp, JSON.stringify(value, null, 2) + '\n')
  renameSync(tmp, path)
}

/** Read a JSON file; missing → fallback, corrupt → fallback (corrupt state is replaced on write). */
function readJson(path, fallback) {
  let raw
  try {
    raw = readFileSync(path, 'utf8')
  } catch {
    return fallback
  }
  try {
    const v = JSON.parse(raw)
    return v && typeof v === 'object' ? v : fallback
  } catch {
    return fallback
  }
}

/** Load, mutate and persist the session state. fn(state) returns the hook result. */
export function updateSession(sessionId, fn, env = process.env) {
  if (!validSessionId(sessionId)) throw new Error('token-guard: invalid session_id')
  const path = join(stateDir(env), `${sessionId}.json`)
  return withLock(path, () => {
    const state = { ...freshState(), ...readJson(path, {}) }
    if (!Array.isArray(state.pending)) state.pending = []
    const result = fn(state)
    writeAtomic(path, state)
    return result
  })
}

export function deleteSession(sessionId, env = process.env) {
  if (!validSessionId(sessionId)) return
  const path = join(stateDir(env), `${sessionId}.json`)
  rmSync(path, { force: true })
  try { rmdirSync(path + '.lock') } catch {}
}

export const FIRING_KINDS = [
  'stepBudget', 'contextBudget', 'verifyChurn',
  'blockedBashStreaks', 'blockedOutsideMutation', 'offloadAsk',
]

export const EMPTY_METRICS = Object.freeze({
  stepBudget: 0, contextBudget: 0, verifyChurn: 0,
  blockedBashStreaks: 0, blockedOutsideMutation: 0, offloadAsk: 0,
  total: 0, sessions: 0, firstFiring: null, lastFiring: null, lastSessionId: null,
})

/**
 * Count one firing. `newSession` is true on the first firing of a session
 * (tracked in the session state, so interleaved sessions are not over-counted).
 */
export function bumpMetrics(kind, sessionId, newSession, env = process.env, now = new Date()) {
  const path = metricsPath(env)
  return withLock(path, () => {
    const m = { ...EMPTY_METRICS, ...readJson(path, {}) }
    const ts = now.toISOString()
    m[kind] = (Number(m[kind]) || 0) + 1
    m.total = (Number(m.total) || 0) + 1
    if (m.firstFiring === null) m.firstFiring = ts
    m.lastFiring = ts
    if (newSession) m.sessions = (Number(m.sessions) || 0) + 1
    m.lastSessionId = sessionId ?? null
    writeAtomic(path, m)
    return m
  })
}

export function readMetrics(env = process.env) {
  return { ...EMPTY_METRICS, ...readJson(metricsPath(env), {}) }
}
