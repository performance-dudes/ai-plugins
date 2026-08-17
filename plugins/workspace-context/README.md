# workspace-context plugin

Use this companion plugin when a repository or workspace is large enough that
agents need searchable, bounded context instead of repeatedly scanning the
filesystem. A directory containing multiple sibling repositories is one
important use case, but the pattern also applies to a single large monorepo,
documentation repository, infrastructure repository, or generated-code-heavy
project.

This plugin does **not** contain Context Mode itself. Install the external
`context-mode` runtime first, then install this companion plugin from the public
marketplace:

```bash
npm install -g context-mode
claude plugin marketplace add mksglu/context-mode
claude plugin install context-mode@context-mode
claude plugin install workspace-context@ai-plugins
```

The global `context-mode` executable is required by the generated indexing
hooks. Installing only the Claude Code plugin does not provide that executable.

## What it helps with

- Setting up a project- or workspace-level Context Mode index for large
  repositories and sibling repositories
- Creating a root `AGENTS.md` that routes agents to `ctx_search` before broad
  manual searches
- Creating a repository-level `sessionStart` hook under `.github/hooks/`
- Reporting a successful index with its source label, file count, and section
  count directly to the Claude Code session
- Keeping project identity, source labels, extension allowlists, and exclusions
  stable across sessions
- Preserving nearer repository-specific `AGENTS.md` files without duplicating
  their instructions

## What the setup creates

When explicitly asked to set up project or workspace indexing, the
`workspace-context` skill creates and adapts:

```text
<project-or-workspace-root>/
├── AGENTS.md
└── .github/hooks/
    ├── reindex-workspace.json
    ├── reindex-workspace.sh
    └── reindex-workspace.ps1
```

The generated hook is intentionally project-local. The plugin does not
register a global indexing hook because a global hook would not know which
project or parent directory, repositories, source label, file policy, or index
size a developer intends to use.

## Explicit skill invocation

This skill is intentionally manual-only. Start Claude Code from the project or
workspace root, then invoke it explicitly:

```text
/workspace-context:workspace-context
```

Alternatively, select `workspace-context` through `/skills` in Claude Code, then
describe the project or workspace to index.

The skill first checks whether Context Mode is installed, inspects existing
instructions and hooks, preserves existing files, then creates only the
missing or necessary workspace-level files.

## Important scope rule

The root `AGENTS.md` and `.github/hooks/` files are applied when Claude Code is
started from the configured project or workspace root. For a parent workspace,
starting Claude Code inside a child repository does not reliably load the parent
workspace instructions. Use `/cwd /path/to/project-or-workspace` or start a
new session at the configured root.

## Reference templates

- [`AGENTS.md.template`](skills/workspace-context/reference/AGENTS.md.template)
- [`reindex-workspace.json.template`](skills/workspace-context/reference/reindex-workspace.json.template)
- [`reindex-workspace.sh.template`](skills/workspace-context/reference/reindex-workspace.sh.template)
- [`reindex-workspace.ps1.template`](skills/workspace-context/reference/reindex-workspace.ps1.template)
