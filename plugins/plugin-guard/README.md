# plugin-guard

A security gate for Claude Code plugins. Plugins run code on your machine — shell
hooks, MCP servers, and **hooks modules (mods): JavaScript/TypeScript that joins the
engine itself**. An update can turn a harmless plugin into a harmful one without you
noticing. `plugin-guard` checks plugins **when Claude Code starts and whenever a
plugin is loaded again** (update, `/reload-plugins`, hot reload).

| Layer | When | What it does | Can it block? |
|---|---|---|---|
| **Mod gate** — `hooks/register.ts` on `plugin.register` | every hooks module, at load **and every reload/update** | scans the plugin's source, judges the capabilities the engine read off the module (`uses`: calls, events, env vars), pins a SHA-256 of the code | **yes** — refuses the module until you approve exactly that state |
| **Start audit** — `SessionStart` hook → `scan.py` | every session start | scans **all** installed plugins (shell hooks, MCP server commands, scripts, modules) and compares with the last start: new, changed (= updated), removed | no — reports |

Both read the same rules: [`rules/rules.json`](rules/rules.json).

## Install

```
/plugin install plugin-guard@ai-plugins
```

**Order matters.** The gate judges only hooks modules that load **after** it. Install
it first, or — the only full guarantee — deploy it as a **managed plugin** (tier
`prepend`), which loads before every user plugin. The start audit covers the rest:
it sees every installed plugin regardless of order.

## Use

When a module is refused you see a toast and, in `/plugin-guard`:

```
REFUSED  evil-helper@1.0.0  [critical]  ⟳ geändert seit letzter Prüfung
           evil-helper@market · ~/.claude/plugins/cache/… · sha256 ae9bc41daa6a…
           - critical combo:http.fetch+secret-env: liest Geheimnisse UND spricht mit dem Netz
           - high     env:secret-read: liest geheime Umgebungsvariablen — GITHUB_TOKEN
ADMITTED event-trace@0.1.0  [medium]
           - medium   event:*: hängt sich in jedes Event
```

Reviewed it and trust it?

```
/plugin-guard approve evil-helper     # pins exactly this code (hash)
/reload-plugins
/plugin-guard revoke evil-helper      # withdraw
```

An approval is bound to the code's hash: **the next update changes the hash and
needs a new approval.** Approvals are only accepted when you type them yourself
(`origin: composer` or Remote Control) — not from the model, another plugin or a
relayed message, so a prompt injection cannot approve anything.

Setting **Block at** (`/config` → plugin-guard): `high` (default), `critical`, or
`off` (report only).

The start audit by hand, or in CI for a marketplace repository:

```bash
python3 hooks/scripts/scan.py ~/.claude/plugins          # human-readable
python3 hooks/scripts/scan.py --json --fail-at high plugins/   # exit 1 from "high"
```

Its state and last report live in `~/.claude/plugin-guard/` (`PLUGIN_GUARD_STATE_DIR`);
`PLUGIN_GUARD_ROOTS` overrides where it looks (default `~/.claude/plugins` plus
`CLAUDE_CODE_PLUGIN_DIRS`).

## What it checks

Source rules (both layers): pipe-to-shell, decode-and-exec, reverse shells, known
exfiltration endpoints, credential stores (`~/.ssh`, `~/.aws/credentials`, Keychain…),
reading secret env vars, dynamic code (`eval`, `new Function`, `child_process`),
persistence (crontab, LaunchAgents, shell rc files), permission bypass, writing Claude
Code settings, `rm -rf ~`, long encoded blobs, unpinned `npx -y`/`uvx` packages.

Capabilities (mod gate only, read exactly by the engine): starting processes,
`env.set` (critical for `PATH`, `NODE_OPTIONS`, `LD_PRELOAD`, proxies, CA certs…),
network, hooks that can change permission decisions (`tool.check`) or settings, rewrite
the system prompt or the conversation, `*`; and combinations — **secret + network is
critical**, file read + network is high.

## Limits — read these

- **Heuristics, not a proof.** A determined attacker can write code that no pattern
  matches. The gate raises the bar and makes every change visible; it does not
  replace reading a plugin before trusting it.
- **A refused module's `register()` has already run** — in its sandbox, where `$` is
  still empty. Refusal keeps every hook, tool, command and noun of it out of the
  session.
- **Shell hooks and MCP servers cannot be blocked** by a plugin; the start audit
  reports them. Prompt content (skills, agents, `*.md`) is not scanned.
- Built-in (`builtin`) and administrator-managed plugins are not judged.

## Contents

| Path | What |
|---|---|
| `hooks/hooks.json` | `modules` (the gate) and `hooks.SessionStart` (the audit) |
| `hooks/register.ts` | The mod: `plugin.register` gate, hash pinning, `/plugin-guard` |
| `hooks/scripts/audit.sh`, `scan.py` | The start audit (Python 3 standard library only) |
| `rules/rules.json` | The one rule set both layers read |
| `tests/guard.test.ts` | Mod tests, `claude plugin test plugins/plugin-guard` |
| `tests/validate.sh` | Plugin suite: static, rules on generated fixtures, audit, engine checks |

Spec: [`specs/plugin-guard/`](../../specs/plugin-guard/0001_product_plugin-guard.md) ·
Docs: [`docs/plugin-guard.md`](../../docs/plugin-guard.md)
