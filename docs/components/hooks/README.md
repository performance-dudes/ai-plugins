# Component: Hooks

> Small programs that run **automatically** when something happens in Claude Code.

## What it is

A hook is a small program that runs automatically on a specific **event** (for
example, "before a tool is used"). A hook can log, add context, or **block** an
action.

## File & format

- **Config:** `example/hooks/hooks.json` (here `hooks.json.example`) — says which
  event runs which program.
- **Program:** usually a `.sh` in `hooks/scripts/` — this is **executed**.

## How a hook "speaks" (the key idea)

A hook receives the event details as **JSON on standard input (stdin)** and replies
through its **exit code**:

| Exit code | Meaning |
|-----------|---------|
| `0` | OK / allow — optional JSON on stdout for extra info |
| `2` | **block** — the stderr message is sent back as the reason |
| other | non-blocking error (only logged) |

Some events also allow a **JSON reply** on stdout, e.g. for `PreToolUse`:
`permissionDecision` = `allow` / `deny` / `ask`, or `updatedInput` to rewrite the
tool's input.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | `hooks.json` at **session start** (and automatically on change). |
| Who triggers it? | The **events**, automatically. |
| Where does it run? | The hook program is **executed** by the OS. |

Because hooks run automatically, the example ships them defused as `.example`.

## The event types (there are 24+)

The example shows only **one** (`PreToolUse`). Here is the whole family, grouped:

| Group | Events | When |
|-------|--------|------|
| **Session** | `SessionStart`, `SessionEnd`, `Setup` | start / end of a session |
| **Input** | `UserPromptSubmit`, `UserPromptExpansion` | you send something / a `/`-command expands |
| **Tools** | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied` | around every tool call |
| **Response** | `Stop`, `StopFailure`, `MessageDisplay` | Claude finishes a reply / shows text |
| **Helpers & tasks** | `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle` | subagents and tasks |
| **Files & environment** | `FileChanged`, `CwdChanged`, `ConfigChange`, `InstructionsLoaded` | a file/folder/config changes |
| **Worktrees** | `WorktreeCreate`, `WorktreeRemove` | git worktrees |
| **Context** | `PreCompact`, `PostCompact` | before/after the history is summarised |
| **MCP forms** | `Elicitation`, `ElicitationResult` | an MCP server asks for input |
| **Hints** | `Notification` | Claude Code shows a notification |

Best events to start with: **`PreToolUse`** (before a tool — can block),
**`PostToolUse`** (after — can add context), **`UserPromptSubmit`** (before Claude
sees your input), **`SessionStart`** (session begins).

## In the example plugin (PR #1)

`hooks/scripts/example-pretooluse.sh` is harmless: it logs to stderr and exits `0`
(allow). Test it **without Claude**:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' \
  | bash example/hooks/scripts/example-pretooluse.sh ; echo "exit=$?"
```
