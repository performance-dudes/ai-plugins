/**
 * Pure decision logic for the token-guard plugin. No opencode imports here so
 * the rules stay unit-testable and the plugin wiring stays thin.
 */

export interface TokenGuardOptions {
  /** Max consecutive single (un-chained) bash calls before blocking. */
  maxConsecutiveBash?: number
  /** Min edit/write operations expected between verification runs. */
  minEditsPerVerify?: number
  /** Soft step budget per session before nudging to compact/split. */
  stepBudget?: number
  /** Soft context budget (input tokens incl. cache read) before nudging. */
  contextBudgetTokens?: number
}

export const DEFAULTS: Required<TokenGuardOptions> = {
  maxConsecutiveBash: 8,
  minEditsPerVerify: 3,
  stepBudget: 200,
  contextBudgetTokens: 150_000,
}

export type BashKind = 'verify' | 'chained' | 'single'

const VERIFY_RE =
  /\b(test|tests|lint|typecheck|tsc|vitest|jest|eslint|ruff|pytest|mypy|prettier)\b|--check\b/
const CHAIN_RE = /&&|\|\||;\s*\S+|\bfor\b|\bwhile\b|\bdo\b\s*$/

/** Classify a bash command for rationing purposes. */
export function classifyBash(command: string): BashKind {
  if (VERIFY_RE.test(command)) return 'verify'
  if (CHAIN_RE.test(command)) return 'chained'
  return 'single'
}

export type Decision = { allow: true } | { allow: false; reason: string }

/**
 * Tracks one session's tool-call pattern and decides when the agent is
 * burning steps: one-command-per-step bash loops and verify-after-every-edit
 * churn. Both multiply provider steps, and every step re-reads the whole
 * (cached) conversation — that is the real token cost driver.
 */
export class Guard {
  readonly opts: Required<TokenGuardOptions>
  private consecutiveSingleBash = 0
  private editsSinceVerify = 0
  private steps = 0
  private stepNudged = false
  private contextNudged = false

  constructor(opts: TokenGuardOptions = {}) {
    this.opts = { ...DEFAULTS, ...opts }
  }

  /** Call before a bash tool executes. Blocks un-batched call streaks. */
  onBashBefore(command: string): Decision {
    const kind = classifyBash(command)
    if (kind !== 'single') {
      if (kind === 'verify') this.editsSinceVerify = 0
      this.consecutiveSingleBash = 0
      return { allow: true }
    }
    this.consecutiveSingleBash++
    if (this.consecutiveSingleBash > this.opts.maxConsecutiveBash) {
      const streak = this.consecutiveSingleBash
      this.consecutiveSingleBash = 0 // let the next streak start fresh after the block
      return {
        allow: false,
        reason:
          `token-guard: ${streak} consecutive single-purpose bash calls. ` +
          'Every tool step re-reads the full (cached) conversation, so one-command-per-step is the ' +
          'most expensive possible pattern. Chain dependent commands with &&, batch independent ' +
          "ones in a parallel tool block, or fold this into the next call — then continue.",
      }
    }
    return { allow: true }
  }

  /** Call after a verify-style command ran; returns a nudge when premature. */
  onVerifyAfter(_command: string): string | null {
    const edits = this.editsSinceVerify
    this.editsSinceVerify = 0
    if (edits === 0 || edits >= this.opts.minEditsPerVerify) return null
    return (
      `token-guard: verification ran after only ${edits} edit(s). ` +
      'Batch more changes between test/lint runs — verify at milestones, not after every edit.'
    )
  }

  /** Call on every edit/write tool call. */
  onEdit(): void {
    this.editsSinceVerify++
  }

  /** Call once per assistant message; returns a nudge at the step budget. */
  onAssistantStep(): string | null {
    this.steps++
    if (this.stepNudged || this.steps <= this.opts.stepBudget) return null
    this.stepNudged = true
    return (
      `token-guard: ${this.steps} provider steps in this session. ` +
      'Long sessions re-read a huge cached context on every step. ' +
      'Wrap up the current subtask, then /compact or start a fresh session.'
    )
  }

  /** Call with the latest context size; returns a one-shot nudge at the budget. */
  onContextSize(inputTokens: number): string | null {
    if (this.contextNudged || inputTokens < this.opts.contextBudgetTokens) return null
    this.contextNudged = true
    return (
      `token-guard: context is at ${(inputTokens / 1000).toFixed(0)}k tokens. ` +
      'Each further step pays for all of it again. Finish the current subtask and compact, ' +
      'or delegate remaining exploration to a subagent.'
    )
  }
}

export function optionsFromEnv(env: NodeJS.ProcessEnv = process.env): TokenGuardOptions {
  const int = (v: string | undefined): number | undefined =>
    v === undefined || v === '' ? undefined : Number.parseInt(v, 10)
  const opts: TokenGuardOptions = {
    maxConsecutiveBash: int(env.TOKEN_GUARD_MAX_CONSECUTIVE_BASH),
    minEditsPerVerify: int(env.TOKEN_GUARD_MIN_EDITS_PER_VERIFY),
    stepBudget: int(env.TOKEN_GUARD_STEP_BUDGET),
    contextBudgetTokens: int(env.TOKEN_GUARD_CONTEXT_BUDGET),
  }
  const clean: TokenGuardOptions = {}
  if (opts.maxConsecutiveBash !== undefined) clean.maxConsecutiveBash = opts.maxConsecutiveBash
  if (opts.minEditsPerVerify !== undefined) clean.minEditsPerVerify = opts.minEditsPerVerify
  if (opts.stepBudget !== undefined) clean.stepBudget = opts.stepBudget
  if (opts.contextBudgetTokens !== undefined) clean.contextBudgetTokens = opts.contextBudgetTokens
  return clean
}
