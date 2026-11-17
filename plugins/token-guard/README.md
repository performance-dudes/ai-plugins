# token-guard

A Claude Code plugin that guards long agent sessions against **token burn**:

> cost ≈ provider steps × context size

Every step re-reads the whole conversation (mostly from cache, but cache reads still
count against cost and quota). token-guard attacks the behaviours that blow up that
product and puts soft budgets on session length and context size. It is a
**tripwire, not an autopilot**: it refuses one tool call with a reason, or tells the
model something, and never rewrites the session.

The Claude Code port of [`opencode-token-guard`](../opencode/opencode-token-guard/).
Spec: [`specs/token-guard/0001_product_token-guard.md`](../../specs/token-guard/0001_product_token-guard.md).

## Guards

| Guard | Hook | What happens | Default |
|---|---|---|---|
| Bash rationing | `PreToolUse` | the (N+1)-th consecutive single-purpose Bash call is refused; the reason tells the model to chain with `&&` or batch in parallel. Chained and verification commands never count. | N = **8** |
| Project escape | `PreToolUse` | a Bash command that writes outside the project root is refused. `/tmp`, `/private/tmp`, `/dev`, `/var/folders` are fine. | always on |
| Verify throttle | `PostToolUse` | the model is told when a test/lint/typecheck ran after fewer than N edits | N = **3** |
| Step budget | `PostToolUse`, `Stop` | one note when the session passes N assistant steps | N = **200** |
| Context budget | `PostToolUse`, `Stop` | one note when the context passes N tokens (input + cache read + cache creation) | N = **150 000** |
| Offload ask | `Stop` | a note when the assistant asks the user to do in-project work themselves | always on |

Notes from `PostToolUse` reach the model immediately. Notes from `Stop` (end of a turn)
are shown to you right away and handed to the model with your next prompt.

## Install

```bash
claude plugin marketplace add performance-dudes/ai-plugins   # once, user scope
```

Then install it once (`claude plugin install token-guard@ai-plugins`) and enable
`token-guard@ai-plugins` in the project's `.claude/settings.json` (`enabledPlugins`).
The marketplace serves `main`, so this only works once the plugin is merged there.

To check that it is active in a session: `/token-guard:token-guard` exists, and
`/hooks` lists its hooks (`PreToolUse`, `PostToolUse`, `Stop`, `UserPromptSubmit`,
`SessionEnd`). Enabled in settings alone is
not enough: run `/reload-plugins` or start a new session.

To try it from a checkout without installing (Claude Code keeps its data under
`~/.claude/plugins/data/token-guard-inline`):

```bash
claude --plugin-dir /path/to/ai-plugins/plugins/token-guard
```

Requires **node ≥ 18** on `PATH`. Without node the hooks exit silently and the plugin
does nothing.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `TOKEN_GUARD_MAX_CONSECUTIVE_BASH` | `8` | single Bash calls in a row before refusing |
| `TOKEN_GUARD_MIN_EDITS_PER_VERIFY` | `3` | edits expected between verification runs |
| `TOKEN_GUARD_STEP_BUDGET` | `200` | assistant steps before the session-length note |
| `TOKEN_GUARD_CONTEXT_BUDGET` | `150000` | context tokens before the context note |
| `TOKEN_GUARD_METRICS_PATH` | `~/.claude/token-guard-metrics.json` | firing counters |

`0` switches a guard off. Only whole numbers count; anything else falls back to the
default.

**Workspaces that require "one command at a time"** (for example the Performance Dudes
workspace `CLAUDE.md`) clash with Bash rationing. Set
`TOKEN_GUARD_MAX_CONSECUTIVE_BASH` higher or to `0` there.

## Stats

`/token-guard:token-guard` prints all-time firing counts per guard, the number of sessions with a
firing, the period, and a clearly labelled rough estimate of steps saved.

## Files it writes

- `~/.claude/token-guard/sessions/<session_id>.json` — per-session counters, deleted at session end.
- `~/.claude/token-guard-metrics.json` — firing counters (schema as in the opencode plugin).

## Differences from the opencode plugin

Same guards, thresholds and variable names. Deliberate differences (spec §6a):
the verify throttle actually fires (it never could in opencode), `/tmp` itself is
inside the allowlist, `0` means off, the offload detector is broader and ignores the
agent's own first-person sentences, and notes reach the model instead of only a log.

## License

MIT
