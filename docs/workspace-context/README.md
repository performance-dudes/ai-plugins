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

## Verifying a fresh index — the two traps

Both were measured while setting the plugin up on a real repository, and both make
the obvious check unreliable rather than merely imprecise.

**A freshly created index is not reachable over MCP from the session that created
it.** The CLI found the indexed passages immediately, `ctx_search` found nothing
from that index in the same session. That is why indexing runs as a `sessionStart`
hook: it happens before the MCP server needs the content. Rebuilding by hand
requires a new session.

**`ctx_search` blends the file index with auto-captured session memory.** Results
tagged `[current-session | … | batch:…]` come from memory. A verification that
lands there proves nothing about the index and reads exactly like a pass — the
content is right, the source is wrong.

The skill therefore prescribes a **falsifiable** check: search the CLI for a term
that was never in session context and confirm the `Source:` line. The same logic
applies to the exclusions — "no results" is also what a broken search returns, so
the term has to appear in a legitimate file too, and the search must return that
one and not the excluded one.
