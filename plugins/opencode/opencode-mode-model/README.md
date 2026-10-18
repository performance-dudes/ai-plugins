# opencode-mode-model

An [opencode](https://opencode.ai) plugin that pins **one model to plan mode** and **another to build mode** — and keeps it pinned across restarts.

Plan a feature with a strong reasoning model; implement it with a fast coding model. Without this plugin, setting `agent.plan.model` / `agent.build.model` in `opencode.json` can silently fall back after a restart (typically because the model isn't declared under its provider). This plugin re-asserts both models on every startup and registers them with their provider so they always resolve.

## Configure

Set two environment variables in the shell opencode runs in (each in `provider/model-id` form):

```sh
export OPENCODE_PLAN_MODEL="zai/glm-5.2"   # used for planning
export OPENCODE_BUILD_MODEL="zai/glm-4.7"  # used for implementation
```

Only `plan`, only `build`, or both may be set. If neither is set, the plugin does nothing.

## Install

### From npm

```jsonc
// opencode.json (~/.config/opencode/opencode.json for global)
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-mode-model"]
}
```

opencode installs npm plugins automatically with Bun at startup.

### From a local file (global)

```sh
npm install -g opencode-mode-model   # or: pnpm add -g opencode-mode-model
mkdir -p ~/.config/opencode/plugins
ln -s "$(npm root -g)/opencode-mode-model/dist/index.js" \
      ~/.config/opencode/plugins/mode-model.js
```

### From source (dev)

```sh
git clone https://github.com/performance-dudes/ai-plugins.git
cd ai-plugins/plugins/opencode/opencode-mode-model
pnpm install && pnpm build
# then either reference it in opencode.json via a local path,
# or copy/symlink dist/index.js into ~/.config/opencode/plugins/
```

Restart opencode after installing.

## How it works

On startup, opencode calls the plugin's `config` hook with the live merged config. The plugin:

1. Reads `OPENCODE_PLAN_MODEL` / `OPENCODE_BUILD_MODEL`.
2. For each, ensures the model id is declared under its provider (`cfg.provider.<provider>.models.<id>`), injecting `{ name: <id> }` only when missing. This is the part that prevents silent fallback for custom (OpenAI-compatible) providers.
3. Sets `cfg.agent.plan.model` / `cfg.agent.build.model`.

Because opencode's `plan` and `build` are distinct primary agents that each carry their own `model`, switching mode in the TUI then uses the right model automatically.

> Note: opencode has no runtime API to change a running session's model. This plugin enforces the mapping at startup, which is the only fully-reliable hook. Within a session, mode switches follow each agent's pinned model.

## Troubleshooting

- **Model still falls back after restart.** Confirm the variable is actually exported in the environment opencode was launched from (`echo $OPENCODE_BUILD_MODEL`), and that the `provider/model-id` matches an enabled provider. The plugin can only register models for providers you've already declared in `provider.*`; for built-in catalog providers the model must be one opencode already knows.
- **Nothing happens.** At least one of the two env vars must be set, and opencode must be restarted after install.

## License

MIT

## TODO

- [ ] Submit PR to opencode docs ecosystem page: https://opencode.ai/docs/ecosystem (add to plugins table)
- [ ] Submit PR to awesome-opencode repo: https://github.com/awesome-opencode/awesome-opencode (add to plugins section)
- [ ] Tag repository with relevant topics (e.g., opencode, plugin, mode-model, llm) for better GitHub discoverability