# event-trace

See what Claude Code actually does. `event-trace` subscribes to **every hook event**
and **every mod event** and writes each one that fires — name, order, origin,
duration, input and result — to JSONL log files. It changes nothing: every event is
passed through untouched.

Two layers, side by side:

| Layer | Mechanism | Sees | Log |
|---|---|---|---|
| **Hooks** | classic command hooks in `hooks/hooks.json` → `hooks/scripts/log-hook.sh` | the 31 settings-hook events (`SessionStart`, `PreToolUse`, `Stop`, …) as JSON on stdin | `<session>.hooks.jsonl` |
| **Mods** | function-hooks module `hooks/register.ts` with `on("*")` | every engine event (`tool.call`, `turn.step`, `ui.render`, `prompt.compose`, …), the hook events again as `classic.<Event>`, every `$` call of every plugin (`fs.read`, `http.fetch`, `env.get`, …), plus `telemetry.*` | `<session>.mods.<load>-<part>.jsonl` |

Logs go to `$EVENT_TRACE_DIR`, default `~/.claude/event-trace/`.

## Install

```
/plugin install event-trace@ai-plugins
```

Or for one session from a checkout: `claude --plugin-dir plugins/event-trace`.

This is a learning and debugging tool. `on("*")` runs on every redraw, too — disable
the plugin when you are done looking.

## Use

Work normally, then:

```
/event-trace
```

prints how often each mod event fired and where both logs are. To read the logs:

```bash
cd ~/.claude/event-trace
# hook layer: what fired, in order
jq -r '[.ts, .event] | @tsv' <session>.hooks.jsonl
# mod layer: one turn, without the redraw noise
jq -c 'select(.event | test("^(ui|command\\.describe)") | not) | {seq, event, origin, ms, outcome}' <session>.mods.*.jsonl
```

A line of the mod log:

```json
{"ts":"…","layer":"mod","seq":312,"event":"tool.call","origin":"engine/core","ms":135,"outcome":"ok",
 "input":{"command":"echo hallo","tool":"Bash","tool_use_id":"toolu_…"},
 "result":{"text":"hallo","isReadOnly":true,"result":{"stdout":"hallo", …}}}
```

## What it does not do

- **No hooks on `WorktreeCreate` / `WorktreeRemove`.** A command hook there *replaces*
  git's worktree handling and has to print the new path — a logger would break
  worktrees. The mod layer still sees both as `classic.WorktreeCreate/Remove`.
- **No stdout from the hook script**, always exit 0: on `SessionStart` and
  `UserPromptSubmit`, stdout would land in the model's context; exit 2 would block.
- **No secrets in the log**: values under keys like `token`, `authorization`,
  `api_key`, `cookie` and `env.get` results for such variables are written as
  `[redacted]`. Prompts, tool input and output are logged — treat the folder as private.

## Contents

| Path | What |
|---|---|
| `hooks/hooks.json` | `hooks` (31 command hooks) and `modules` (the mod) in one file |
| `hooks/scripts/log-hook.sh` | The command hook: appends one JSON line per event |
| `hooks/register.ts` | The mod: `on("*")`, `on("telemetry.*")`, buffered writer, `/event-trace` |
| `tests/trace.test.ts` | Mod tests, `claude plugin test plugins/event-trace` |
| `tests/validate.sh` | Plugin suite (static, script-run, engine checks) |

Spec: [`specs/event-trace/`](../../specs/event-trace/0001_product_event-trace.md) ·
Docs: [`docs/event-trace.md`](../../docs/event-trace.md)
