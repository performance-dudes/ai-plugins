---
name: workspace-context
description: |
  Set up and maintain a Context Mode index for a large repository or a parent workspace containing sibling repositories.
  Use when: 'set up Context Mode project indexing', 'set up Context Mode workspace indexing',
  'index a large repository', 'index sibling repositories', 'create workspace AGENTS.md and session start hook',
  'configure cross-repository Claude Code context', 'make the project searchable'.
disable-model-invocation: true
---

# Context Mode project/workspace setup

Use this skill only after the user explicitly asks to set up or change
project- or workspace-level indexing. It creates a small, reviewable layer
around the external `context-mode` plugin; it does not replace or vendor
Context Mode.

## Prerequisite: install Context Mode

Check both the global Context Mode executable and the Claude Code integration before
creating project files. If either is missing, recommend:

```bash
npm install -g context-mode
claude plugin marketplace add mksglu/context-mode
claude plugin install context-mode@context-mode
```

The generated hooks call the global `context-mode` executable directly;
installing only the Claude Code plugin is not sufficient.

In Claude Code, enable `context-mode@context-mode` at the workspace level. The
companion plugin is not a dependency manager and cannot silently install the
external runtime.

## Setup contract

1. Resolve the intended **project/workspace root**. It may be a large single
   repository, monorepo, documentation or infrastructure repository, or the
   parent directory that contains sibling repositories.
2. Inspect existing `AGENTS.md`, `.github/hooks/`, Claude Code instructions, and
   ignore files. Never overwrite an existing `AGENTS.md` or hook without
   preserving accurate content and showing the required diff.
3. Choose a stable source label such as `<project-name> context`.
4. Set `--project` to the absolute project/workspace root so each indexed
   project or workspace has an isolated Context Mode content store.
5. Create or update a root `AGENTS.md` that describes the actual project or
   workspace, not the template. Write the observed root path, project kind,
   repository scope, source label, hook path, indexed content, and exclusions
   into the file. For a single repository, do not describe it as a sibling
   repository workspace; for a multi-repository parent, state the repository
   count or scope when known. The file must tell agents to query:

   ```text
   ctx_search(queries: ["focused question"], source: "<project-name> context")
   ```

   The file must also say when to use `ctx_execute` or `ctx_execute_file` for
   counting, filtering, comparison, or summarization. Replace every
   `<placeholder>` before writing the file.
6. Create a repository-level `.github/hooks/*.json` with a `sessionStart`
   command and Bash/PowerShell scripts. The hook must:
   - resolve its root from the script location;
   - fail clearly when `context-mode` is not installed;
   - use an explicit extension allowlist;
   - respect `.gitignore` and exclude generated directories, caches, state,
     logs, databases, binaries, data files, and common credential files;
   - set a bounded file/depth limit and a visible timeout.
   - make the Bash script executable (`chmod +x`) and verify that permission;
   - emit one compact JSON `hookSpecificOutput` status only after a successful
     index, including `hookEventName: "SessionStart"`, the exact source label,
     and the reported file/section counts;
   - report a clear failure message to stderr and return a non-zero exit code
     when Context Mode is unavailable, indexing fails, or completion counts
     cannot be parsed.

   A successful hook should emit a single-line payload in this shape:

   ```json
   {"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"[context-mode] index ready - <source>: <files> files / <sections> sections indexed."}}
   ```

   Do not pass the raw `context-mode index` output through as hook output; the
   CLI output is human-readable and may not be valid hook JSON.
7. Run the index command once, then verify it as described under **Verifying the
   index** — not with `ctx_search`, which is invalid from the session that built
   the index. Also verify that the hook emits the ready status with file and
   section counts.
8. Report every created file and the exact source label in the final diff.

## Verifying the index

`ctx_search` from the session that built the index proves nothing — in either
direction:

- **It fails on a healthy index.** An index created after session start is not
  reachable over MCP in that session. This is why indexing belongs in the
  `sessionStart` hook; a manual rebuild needs a new session.
- **It passes on an absent one.** `ctx_search` also serves auto-captured session
  memory. Results tagged `[current-session | … | batch:…]` are memory, not the
  file index.

Verify instead:

1. Pick a term that sits in a file and was **never in this session's context** —
   a colleague's or subagent's wording, a passage nobody opened.
2. Run `context-mode search "<term>"` from the project root. The result must carry
   a `Source:` line with the expected path. That line is the only thing separating
   a file hit from a memory hit.
3. Check the hook payload separately (step 6) — it answers a different question.

**Exclusions need the same care.** Searching for a secret and finding nothing
proves nothing: a broken search returns nothing too. Pick a term that appears in
an excluded **and** in a legitimate file — an environment-variable name usually
does. The search must return the legitimate files and not the excluded one.

## AGENTS.md content contract

The generated root `AGENTS.md` should contain only project- or
cross-workspace guidance:

- the number or type of sibling repositories, if known;
- the stable Context Mode source label;
- `ctx_search` before `grep`, `rg`, `find`, or broad directory listings;
- `ctx_execute` / `ctx_execute_file` for data-heavy analysis;
- exact file reads only after the index locates the target;
- the project/workspace-root startup requirement;
- the high-level index exclusions.
- the session-start hook's successful index status and failure behavior.
- the requirement to surface a confirmed index status in the first response;

Do not copy child repository build commands, architecture rules, or local
conventions into the parent file. Nearest repository-specific `AGENTS.md`
files remain authoritative for their own repository.
Do not copy the reference template verbatim: adapt its wording to the
observed project kind and verify that no template placeholders remain.

## Hook and performance rules

Keep indexing project-local rather than registering a global plugin hook.
The project or workspace knows its own root, source label, file policy, and
size limits.
Use the generated templates in `reference/` as a starting point, then adapt
the extension list and exclusions to the actual workspace.

Context Mode refreshes changed file-backed sources during search. The current
CLI keeps cached results for deleted files, so do not claim that a session-start
reindex is a complete deletion reconciliation. If deletion accuracy is a
requirement, raise it as a Context Mode capability gap instead of modifying
its SQLite database directly.

## Safety

- Do not index secrets, credentials, private keys, tokens, environment files,
  Terraform state/plan files, databases, local caches, or user data by default.
- Do not follow symlinks unless the workspace owner explicitly approves it.
- Do not scan arbitrary parent directories; resolve and confirm the requested
  workspace root.
- Do not add a plugin-level `sessionStart` hook for this workflow.
