import type { Plugin } from '@opencode-ai/plugin'
import { Guard, classifyBash, optionsFromEnv } from './guard.js'

export * from './guard.js'

interface ToolInput {
  tool: string
}

interface ToolArgs {
  command?: string
  [k: string]: unknown
}

interface MessageInfo {
  id?: string
  role?: string
  tokens?: { input?: number; output?: number; cacheRead?: number; cacheWrite?: number }
  cost?: { [k: string]: unknown }
}

/**
 * Guards long agent sessions against token burn. Every provider step re-reads
 * the full (cached) conversation, so the plugin attacks step count and context
 * size directly:
 *
 * - blocks streaks of single-purpose bash calls (chain/batch instead),
 * - nudges when verification runs happen after too few edits,
 * - nudges at a step budget and a context-size budget per session.
 *
 * Thresholds are configurable via TOKEN_GUARD_* environment variables.
 */
const TokenGuard: Plugin = async ({ client }) => {
  const guard = new Guard(optionsFromEnv())
  const seenMessages = new Set<string>()

  const notify = async (message: string) => {
    await client.app.log({ body: { service: 'token-guard', level: 'warn', message } }).catch(() => {})
  }

  return {
    'tool.execute.before': async (input: ToolInput, output: { args: ToolArgs }) => {
      if (input.tool === 'bash' && typeof output.args.command === 'string') {
        const decision = guard.onBashBefore(output.args.command)
        if (!decision.allow) throw new Error(decision.reason)
      }
      if (input.tool === 'edit' || input.tool === 'write') guard.onEdit()
    },

    'tool.execute.after': async (input: ToolInput & { args?: ToolArgs }) => {
      if (input.tool === 'bash' && typeof input.args?.command === 'string') {
        if (classifyBash(input.args.command) === 'verify') {
          const nudge = guard.onVerifyAfter(input.args.command)
          if (nudge) await notify(nudge)
        }
      }
    },

    event: async ({ event }: { event: { type: string; properties?: unknown } }) => {
      if (event.type !== 'message.updated') return
      const info = (event.properties as { info?: MessageInfo } | undefined)?.info
      if (!info || info.role !== 'assistant' || !info.id) return
      if (seenMessages.has(info.id)) return
      seenMessages.add(info.id)

      const stepNudge = guard.onAssistantStep()
      if (stepNudge) await notify(stepNudge)

      const ctx =
        (info.tokens?.input ?? 0) +
        (info.tokens?.cacheRead ?? 0) +
        (info.tokens?.cacheWrite ?? 0)
      const ctxNudge = guard.onContextSize(ctx)
      if (ctxNudge) await notify(ctxNudge)
    },
  }
}

export default TokenGuard
export { TokenGuard }
