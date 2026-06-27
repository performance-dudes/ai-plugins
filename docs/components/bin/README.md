# Component: `bin/` executables  *(not shipped in the example yet)*

> Programs a plugin puts on your PATH while it is enabled.

## What it is

Any executable placed in a plugin's `bin/` folder is added to the Bash tool's
**PATH** while the plugin is enabled — so it can be called like any normal command.

## File & format

- **Folder:** `bin/<executable>` — any executable (a shell script, a compiled
  binary, …).
- **Format:** an **executable file** (not data). A shell script needs a shebang
  (`#!/usr/bin/env bash`) and the executable bit (`chmod +x`).

## Architecture: when available, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it available? | While the plugin is **enabled** (added to PATH at load). |
| Who triggers it? | **Claude** (via the Bash tool) or **you**. |
| Where does it run? | Executed by the **operating system**. |

## Status in the example plugin

**Not shipped yet — this is a gap.** The example plugin from #1 has no `bin/`
folder.

## How you would add it

Create `example/bin/hello`:

```bash
#!/usr/bin/env bash
echo "hello from the example plugin"
```

then `chmod +x example/bin/hello`. Now `hello` is on PATH whenever the plugin is
enabled.
