# workspace-context

`workspace-context` is the public companion plugin for setting up bounded
Context Mode indexing in a large repository or in a parent directory containing
sibling repositories.

## Current behavior

The plugin provides the explicit `workspace-context` skill and four reference
templates. The skill adapts those templates to a user-confirmed project root:

```text
<project-root>/
├── AGENTS.md
└── .github/hooks/
    ├── reindex-workspace.json
    ├── reindex-workspace.sh
    └── reindex-workspace.ps1
```

The external `context-mode` runtime and its Claude Code integration remain
workspace-level dependencies. The plugin does not vendor or install them
silently, and it does not register a global hook.

## Usage

Install the runtime and marketplace dependency once, then install the public
plugin:

```bash
npm install -g context-mode
claude plugin marketplace add mksglu/context-mode
claude plugin install context-mode@context-mode
claude plugin install workspace-context@ai-plugins
```

Start Claude Code at the intended project or workspace root and invoke:

```text
/workspace-context:workspace-context
```

The generated hook emits one compact `SessionStart` status only after a
successful index and reports a non-zero failure when the executable, indexing
operation, or completion counts are unavailable.

See the [plugin README](../../plugins/workspace-context/README.md) and
[skill source](../../plugins/workspace-context/skills/workspace-context/SKILL.md)
for the complete setup contract.
