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
   index**. When the workspace contains sibling repositories, verify a hit from at
   least two of them. Also verify that the hook emits the ready status with file
   and section counts.
8. Report every created file and the exact source label in the final diff.

## Verifying the index

An unfiltered `ctx_search` is not a valid check, in either direction:

- **A miss does not prove a broken index.** Context Mode keeps one store per
  project directory. If `context-mode search` finds a term and `ctx_search` does
  not, the session runs in a different project directory than the one the hook
  indexes — start the session at that root.
- **A hit does not prove the file index.** `ctx_search` also serves auto-captured
  session memory. Every hit is tagged `[current-session | … | <source>]`; only the
  source part tells them apart — `batch:…` is memory, the hook's source label is
  the file index. Always filter by the source label.

Verify instead:

1. From the project root, run `context-mode search "<term>" --source "<source label>"`.
   Every result must carry a `Source:` line with the expected file path — the path
   decides, not the content.
2. In a workspace, repeat with one term from each of at least two sibling
   repositories; each needs its own expected `Source:` path.
3. Check the hook payload separately (step 6) — it answers a different question.

**Exclusions need the same care.** Searching for a secret and finding nothing
proves nothing: a broken search returns nothing too, and `context-mode search`
returns 3 results unless `--limit` is set, so a leaked file can fall off the list.
Pick a term that appears in an excluded **and** in legitimate files — an
environment-variable name usually does:

1. Count the legitimate files first: `rg -l "<term>"` over the hook's allowlisted
   extensions.
2. Search with `context-mode search "<term>" --source "<source label>" --limit 100`.
3. Pass only if every legitimate file appears, the result count stays below the
   limit, and no excluded path appears.

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
