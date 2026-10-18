# ai-plugins
Performance Dudes AI plugins — OpenCode and Claude-Code plugins

## Plugins

### OpenCode Plugins

- [opencode-mode-model](./plugins/opencode/opencode-mode-model/) — Pin one model to plan mode and another to build mode

### Claude-Code Plugins

- [content-craft](./plugins/content-craft/) — Content crafting and editing
- [context-aware](./plugins/context-aware/) — Context-aware operations
- [image-toolkit](./plugins/image-toolkit/) — Image processing toolkit
- [mechanic](./plugins/mechanic/) — Mechanic operations
- [ocr](./plugins/ocr/) — OCR capabilities
- [transcribe](./plugins/transcribe/) — Audio transcription

## Structure

```
ai-plugins/
├── plugins/
│   ├── opencode/         # OpenCode plugins
│   └── (root level)      # Claude-Code plugins
```

## Development

```sh
# Install dependencies
pnpm install

# Build all plugins
pnpm build

# Clean all builds
pnpm clean
```
