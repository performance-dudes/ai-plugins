#!/usr/bin/env node
// Deterministic firing report for /token-guard:token-guard. Reads the metrics file and prints
// counts per kind, sessions, the time span and a clearly labelled rough estimate.

import { metricsPath, readMetrics } from './lib/store.mjs'

// Rough, labelled heuristics — not measurements.
const STEPS_SAVED_PER_BASH_BLOCK = 4 // a blocked streak is usually folded into one chained call
const CONTEXT_TOKENS_PER_STEP = 60_000 // typical cached context re-read per step in a long session

const LABELS = {
  blockedBashStreaks: 'blocked Bash streaks',
  blockedOutsideMutation: 'blocked out-of-project mutations',
  verifyChurn: 'verify-churn nudges',
  stepBudget: 'step-budget nudges',
  contextBudget: 'context-budget nudges',
  offloadAsk: 'offload-ask nudges',
}

export function report(m, path) {
  const lines = [`token-guard firing stats (${path})`, '']
  if (!m.total) {
    lines.push('No firings recorded yet.')
    return lines.join('\n')
  }
  const width = Math.max(...Object.values(LABELS).map((l) => l.length))
  for (const [k, label] of Object.entries(LABELS)) lines.push(`  ${label.padEnd(width)}  ${m[k] ?? 0}`)
  lines.push(`  ${'total'.padEnd(width)}  ${m.total}`)
  lines.push('')
  lines.push(`sessions with a firing: ${m.sessions}`)
  lines.push(`period: ${m.firstFiring ?? '—'} → ${m.lastFiring ?? '—'}`)
  const steps = (m.blockedBashStreaks ?? 0) * STEPS_SAVED_PER_BASH_BLOCK
  lines.push('')
  lines.push(
    `ESTIMATE (heuristic, not measured): ~${steps} provider steps saved by Bash blocks ` +
      `≈ ${((steps * CONTEXT_TOKENS_PER_STEP) / 1e6).toFixed(1)}M cached input tokens ` +
      `(assumes ${STEPS_SAVED_PER_BASH_BLOCK} steps per block, ${CONTEXT_TOKENS_PER_STEP / 1000}k tokens per step). ` +
      'Nudges are not counted as savings: whether the model acted on them is not observable.',
  )
  return lines.join('\n')
}

if (process.argv[1]?.endsWith('stats.mjs')) {
  console.log(report(readMetrics(), metricsPath()))
}
