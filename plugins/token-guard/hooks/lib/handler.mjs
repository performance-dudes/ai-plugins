// Hook dispatcher: one function per hook event, pure apart from the state/metrics files.

import {
  checkContextBudget, checkStepBudget, classifyBash, isOffloadAsk, mutatesOutsideProject,
  OFFLOAD_MESSAGE, onBashBefore, onEdit, onVerifyAfter, optionsFromEnv, outsideMutationReason,
} from './guard.mjs'
import { bumpMetrics, deleteSession, updateSession } from './store.mjs'
import { advanceTranscript } from './transcript.mjs'

const EDIT_TOOLS = new Set(['Edit', 'Write', 'NotebookEdit', 'MultiEdit'])

export function handle(input, env = process.env) {
  const event = input?.hook_event_name
  const sid = input?.session_id
  if (event === 'SessionEnd') {
    deleteSession(sid, env)
    return null
  }
  const opts = optionsFromEnv(env)
  const root = env.CLAUDE_PROJECT_DIR || input.cwd || ''

  return updateSession(sid, (state) => {
    const fire = (kind) => {
      try {
        bumpMetrics(kind, sid, !state.metricsSessionCounted, env)
        state.metricsSessionCounted = true
      } catch {}
    }
    const budgets = () => {
      const out = []
      if (typeof input.transcript_path !== 'string') return out
      try {
        advanceTranscript(state, input.transcript_path)
      } catch {
        return out
      }
      const step = checkStepBudget(state, opts)
      if (step) { fire('stepBudget'); out.push(step) }
      const ctx = checkContextBudget(state, opts)
      if (ctx) { fire('contextBudget'); out.push(ctx) }
      return out
    }

    switch (event) {
      case 'PreToolUse': {
        const cmd = input.tool_input?.command
        if (input.tool_name === 'Bash' && typeof cmd === 'string') {
          if (mutatesOutsideProject(cmd, root, env.HOME ?? '')) {
            fire('blockedOutsideMutation')
            return deny(outsideMutationReason(root))
          }
          const d = onBashBefore(state, opts, cmd)
          if (!d.allow) {
            fire('blockedBashStreaks')
            return deny(d.reason)
          }
        } else if (EDIT_TOOLS.has(input.tool_name)) {
          onEdit(state)
        }
        return null
      }

      case 'PostToolUse': {
        const notes = state.pending.splice(0)
        const cmd = input.tool_input?.command
        if (input.tool_name === 'Bash' && typeof cmd === 'string' && classifyBash(cmd) === 'verify') {
          const n = onVerifyAfter(state, opts)
          if (n) { fire('verifyChurn'); notes.push(n) }
        }
        notes.push(...budgets())
        return context('PostToolUse', notes)
      }

      case 'Stop': {
        const notes = budgets()
        const text =
          typeof input.last_assistant_message === 'string' ? input.last_assistant_message : state.lastAssistantText
        const key = state.lastMessageId ?? text
        if (text && key !== state.offloadCheckedId) {
          state.offloadCheckedId = key
          if (isOffloadAsk(text)) { fire('offloadAsk'); notes.push(OFFLOAD_MESSAGE) }
        }
        if (!notes.length) return null
        // The turn is over: show the user now, hand it to the model with the next prompt.
        state.pending.push(...notes)
        return { systemMessage: notes.join('\n') }
      }

      case 'UserPromptSubmit':
        return context('UserPromptSubmit', state.pending.splice(0))

      default:
        return null
    }
  }, env)
}

function deny(reason) {
  return {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    },
  }
}

function context(hookEventName, notes) {
  if (!notes.length) return null
  return { hookSpecificOutput: { hookEventName, additionalContext: notes.join('\n') } }
}
