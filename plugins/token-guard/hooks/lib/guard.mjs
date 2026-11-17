// Pure decision logic for token-guard (Claude Code). Hand-ported from the opencode
// plugin's src/guard.ts. Deliberate deviations are marked "DEVIATION" and listed
// in specs/token-guard/0001_product_token-guard.md §6a.
//
// Unlike the opencode plugin, Claude Code starts a fresh process per hook event,
// so the guard works on a plain, JSON-serialisable state object instead of
// instance fields.

export const DEFAULTS = Object.freeze({
  maxConsecutiveBash: 8,
  minEditsPerVerify: 3,
  stepBudget: 200,
  contextBudgetTokens: 150_000,
})

export function freshState() {
  return {
    consecutiveSingleBash: 0,
    editsSinceVerify: 0,
    steps: 0,
    lastMessageId: null,
    lastContextTokens: 0,
    lastAssistantText: '',
    offloadCheckedId: null,
    transcriptOffset: 0,
    stepNudged: false,
    contextNudged: false,
    metricsSessionCounted: false,
    pending: [],
  }
}

const VERIFY_RE =
  /\b(test|tests|lint|typecheck|tsc|vitest|jest|eslint|ruff|pytest|mypy|prettier)\b|--check\b/
const CHAIN_RE = /&&|\|\||;\s*\S+|\bfor\b|\bwhile\b|\bdo\b\s*$/

/** @returns {'verify'|'chained'|'single'} */
export function classifyBash(command) {
  if (VERIFY_RE.test(command)) return 'verify'
  if (CHAIN_RE.test(command)) return 'chained'
  return 'single'
}

/** PreToolUse for Bash. Mutates state; returns {allow:true} or {allow:false, reason}. */
export function onBashBefore(state, opts, command) {
  const kind = classifyBash(command)
  if (kind !== 'single') {
    // DEVIATION: only the streak resets here. The opencode plugin also zeroed
    // editsSinceVerify, so onVerifyAfter always read 0 and never fired.
    state.consecutiveSingleBash = 0
    return { allow: true }
  }
  if (opts.maxConsecutiveBash === 0) return { allow: true } // DEVIATION: 0 = off
  state.consecutiveSingleBash++
  if (state.consecutiveSingleBash > opts.maxConsecutiveBash) {
    const streak = state.consecutiveSingleBash
    state.consecutiveSingleBash = 0
    return {
      allow: false,
      reason:
        `token-guard: ${streak} consecutive single-purpose Bash calls. ` +
        'Every tool step re-reads the full (cached) conversation, so one-command-per-step is the ' +
        'most expensive possible pattern. Chain dependent commands with &&, batch independent ' +
        'ones in a parallel tool block, or fold this into the next call — then continue.',
    }
  }
  return { allow: true }
}

/** PostToolUse for a verify-style Bash command; returns a nudge or null. */
export function onVerifyAfter(state, opts) {
  const edits = state.editsSinceVerify
  state.editsSinceVerify = 0
  if (opts.minEditsPerVerify === 0) return null
  if (edits === 0 || edits >= opts.minEditsPerVerify) return null
  return (
    `token-guard: verification ran after only ${edits} edit(s). ` +
    'Batch more changes between test/lint runs — verify at milestones, not after every edit.'
  )
}

export function onEdit(state) {
  state.editsSinceVerify++
}

/** Call after the step count was updated; returns a one-shot nudge or null. */
export function checkStepBudget(state, opts) {
  if (opts.stepBudget === 0 || state.stepNudged || state.steps <= opts.stepBudget) return null
  state.stepNudged = true
  return (
    `token-guard: ${state.steps} provider steps in this session. ` +
    'Long sessions re-read a huge cached context on every step. ' +
    'Wrap up the current subtask, then /compact or start a fresh session.'
  )
}

export function checkContextBudget(state, opts) {
  const tokens = state.lastContextTokens
  if (opts.contextBudgetTokens === 0 || state.contextNudged || tokens < opts.contextBudgetTokens) return null
  state.contextNudged = true
  return (
    `token-guard: context is at ${(tokens / 1000).toFixed(0)}k tokens. ` +
    'Each further step pays for all of it again. Finish the current subtask and /compact, ' +
    'or delegate remaining exploration to a subagent.'
  )
}

/* ---------------------------------------------------------------------------
 * Project-escape / offload guards
 * ------------------------------------------------------------------------- */

// DEVIATION: the directory itself is allowed too (opencode required a trailing slash,
// so `cd /tmp && touch x` counted as outside).
const OUTSIDE_ALLOW = [/^\/(private\/)?tmp(\/|$)/, /^\/dev(\/|$)/, /^\/var\/folders(\/|$)/]

const WRITE_HINT_RE =
  />>?|\btee\b|\bsed\b[^&|;]*\s-i|\bperl\b[^&|;]*\s-i|\b(?:mv|cp|ln|mkdir|touch|rm|rmdir|truncate|install|rsync)\b/

const HEREDOC_WRITE_RE =
  /<<-?\s*['"]?[A-Za-z_]+['"]?[\s\S]*?(?:open\s*\([^)]*['"][wa]['"]|json\.dump|yaml\.dump|\.write\s*\(|writeFileSync)/

const PATH_TOKEN_RE = /(?:~|\$HOME)(?:\/[^\s'"&|;]*)?|(?<=^|[\s='"`])(?:\/(?:[A-Za-z0-9._-]+\/)+[A-Za-z0-9._-]*)/g

function isOutside(target, projectRoot, home) {
  const p = target.replace(/^~(?=\/)/, home).replace(/^\$HOME(?=\/)/, home)
  if (!p.startsWith('/')) return false
  if (OUTSIDE_ALLOW.some((re) => re.test(p))) return false
  const root = projectRoot.replace(/\/+$/, '')
  if (!root) return false
  return p !== root && !p.startsWith(root + '/')
}

export function mutatesOutsideProject(command, projectRoot, home = process.env.HOME ?? '') {
  if (!projectRoot) return false
  const outside = (t) => isOutside(t, projectRoot, home)

  for (const m of command.matchAll(/>>?\s*("[^"]+"|'[^']+'|\S+)/g)) {
    const target = m[1].replace(/^["']|["']$/g, '')
    if (target && !target.startsWith('&') && outside(target)) return true
  }

  for (const segRe of [/\b(?:mkdir|touch|rm|tee|ln|truncate)\b[^&|;]*/g, /\bsed\b[^&|;]*\s-i[^&|;]*/g]) {
    for (const m of command.matchAll(segRe)) {
      for (const p of m[0].matchAll(PATH_TOKEN_RE)) if (outside(p[0])) return true
    }
  }

  for (const m of command.matchAll(/\bcd\s+("[^"]+"|'[^']+'|\S+)/g)) {
    const target = m[1].replace(/^["']|["']$/g, '')
    if (!outside(target)) continue
    if (WRITE_HINT_RE.test(command) || HEREDOC_WRITE_RE.test(command)) return true
  }

  return false
}

export function outsideMutationReason(projectRoot) {
  return (
    `token-guard: this command mutates state outside the project root (${projectRoot}). ` +
    'Work for this session belongs inside the project — redo the change in-project with the ' +
    'Edit/Write tools or a project-relative command. Never relocate the work outside the ' +
    'project and never ask the user to run it there; if a permission prompt blocked an ' +
    'in-project action, narrow the command instead.'
  )
}

// DEVIATION (eval-driven, evals/offload/): more verbs (create/do/edit/…, erstelle/leg/mach/…),
// "von Hand"/"händisch", and the `erstell\b` miss on "Erstelle" fixed. Patterns 1–3 and 5–6
// are otherwise the opencode originals.
const OFFLOAD_PATTERNS = [
  /\b(?:run|execute|paste|type|copy|move|carry out|perform|create|do|edit|make|add|delete|write|install|apply)\b[^.!?]{0,120}\b(?:yourself|your own|your terminal|your machine|manually|by hand|outside (?:the|this) (?:project|repo|repository|folder|directory|workspace))\b/i,
  /\b(?:outside (?:the|this) (?:project|repo|repository|folder|directory|workspace))\b[^.!?]{0,120}\b(?:run|execute|paste|type|copy|move|create|edit|perform)\b/i,
  /\bgo (?:outside|up) (?:of )?(?:the|this) (?:project|repo|folder|workspace)\b/i,
  /\b(?:führe|führen|ausführen|einfügen|kopiere|kopieren|verschiebe|verschieben|erstelle?|erstellen|lege?|anlegen|mache?|bearbeite|bearbeiten)\b[^.!?]{0,120}(?:\b(?:selbst|manuell|händisch|in deine[mn] Terminal|außerhalb)\b|\bvon Hand\b)/i,
  /\baußerhalb (?:des|der) (?:Projekts?|Projektordners|Repositorys?|Workspaces?)\b[^.!?]{0,120}\b(?:ausführen|einfügen|kopieren|verschieben|erstellen|bearbeiten)\b/i,
  /\bgehe?\b[^.!?]{0,80}\b(?:außerhalb|hinaus)\b/i,
]

// DEVIATION: a sentence in the first person that does not address the user describes
// the agent's own work ("Next I'll run the linter manually"), not an offload.
const FIRST_PERSON_RE = /(?:^|[^A-Za-z])(?:I|I'll|I've|I'm|I'd)(?![A-Za-z'])|\b(?:we|we'll|let me|let's|ich|wir)\b/i
const ADDRESSES_USER_RE = /\b(?:you|your|please|du|dein\w*|dir|bitte|ihr|euch)\b/i

export function isOffloadAsk(text) {
  return text
    .split(/(?<=[.!?])\s+/)
    .some(
      (s) =>
        !(FIRST_PERSON_RE.test(s) && !ADDRESSES_USER_RE.test(s)) &&
        OFFLOAD_PATTERNS.some((re) => re.test(s)),
    )
}

export const OFFLOAD_MESSAGE =
  'token-guard: the assistant asked the user to run/do work outside the project (or to take ' +
  'over in-project work). In-project work stays in-project: do it with Edit/Write/Bash inside ' +
  'the project root. If a permission prompt blocked an in-project action, retry with a narrower ' +
  'in-project command — never offload it to the user.'

/** DEVIATION: only a whole non-negative integer counts as set; 0 disables a guard. */
export function optionsFromEnv(env = process.env) {
  const int = (v) => (typeof v === 'string' && /^[0-9]+$/.test(v) ? Number(v) : undefined)
  const pick = (v, d) => (v === undefined ? d : v)
  return {
    maxConsecutiveBash: pick(int(env.TOKEN_GUARD_MAX_CONSECUTIVE_BASH), DEFAULTS.maxConsecutiveBash),
    minEditsPerVerify: pick(int(env.TOKEN_GUARD_MIN_EDITS_PER_VERIFY), DEFAULTS.minEditsPerVerify),
    stepBudget: pick(int(env.TOKEN_GUARD_STEP_BUDGET), DEFAULTS.stepBudget),
    contextBudgetTokens: pick(int(env.TOKEN_GUARD_CONTEXT_BUDGET), DEFAULTS.contextBudgetTokens),
  }
}
