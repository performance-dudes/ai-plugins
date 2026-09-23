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

## Verifying a fresh index — three traps

Each makes the obvious check unreliable rather than merely imprecise.

**`ctx_search` and the CLI can look at different stores.** Context Mode keeps one
store per project directory. When `context-mode search` finds indexed passages and
`ctx_search` does not, the session runs in another project directory than the one
the hook indexed — the fix is to start the session at that root, not to rebuild.

**`ctx_search` blends the file index with auto-captured session memory.** Every hit
is tagged `[current-session | … | <source>]`; only the source part separates them.
`batch:…` is memory, the hook's source label is the file index. A verification
that lands on a `batch:` hit reads exactly like a pass — the content is right, the
source is wrong. Filtering by the source label removes those rows.

**`context-mode search` returns 3 results by default.** An exclusion check that
searches for a term and sees only legitimate files proves nothing when the list
was cut off: a leaked file can sit at position four.

The skill therefore prescribes a **falsifiable** check: search with the source
label and confirm each `Source:` path; in a workspace, do it for at least two
sibling repositories. For exclusions, count the legitimate files with `rg -l`
first, search with `--limit 100`, and pass only if every legitimate file appears,
the result count stays below the limit and no excluded path shows up.
