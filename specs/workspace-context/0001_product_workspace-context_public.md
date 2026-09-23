# Product Spec: Public workspace-context plugin

Spec-ID: `SPEC-workspace-context-public` · Status: Implemented — pending review ·
Date: 2026-08-17

## Theme

Publish a generic `workspace-context` Claude Code plugin in the public
Performance Dudes marketplace. The plugin provides explicit setup guidance and
reference templates for Context Mode indexing across a large repository or a
parent workspace containing sibling repositories.

The public plugin must not carry source-repository or client-specific identity,
metadata, installation commands, or documentation.

## User stories and acceptance criteria

### US-WC-1 — Install and discover the public plugin

As a Claude Code user, I want to find and install the workspace indexing
companion from the public marketplace so that I can set up Context Mode without
copying private or source-repository branding.

| ID | Acceptance criterion | Test |
|---|---|---|
| AC-WC-1-1 | The plugin uses the Claude Code layout under `plugins/workspace-context/`, has a valid `.claude-plugin/plugin.json`, and is registered in `.claude-plugin/marketplace.json` with a matching version. | `tests/workspace-context/validate.sh`; `tests/structure/check.sh` |
| AC-WC-1-2 | Plugin metadata, README, skill, and references contain no client names, source plugin name, or source-marketplace installation reference. | `tests/workspace-context/validate.sh` |

### US-WC-2 — Set up bounded workspace indexing

As a repository or workspace owner, I want explicit, manual setup instructions
and adaptable templates so that indexing is project-local, bounded, and
non-destructive.

| ID | Acceptance criterion | Test |
|---|---|---|
| AC-WC-2-1 | The `workspace-context` skill requires explicit invocation, checks the external Context Mode prerequisite, preserves existing instructions and hooks, and documents the generated `AGENTS.md` and `.github/hooks/` contract. | `tests/workspace-context/validate.sh` |
| AC-WC-2-2 | The plugin ships the four reference templates from the source plugin; JSON parses and the Bash hook passes `bash -n`. | `tests/workspace-context/validate.sh` |
| AC-WC-2-3 | The generated hook contract reports a compact success payload and fails clearly when Context Mode or completion counts are unavailable. | `tests/workspace-context/validate.sh` |
| AC-WC-2-4 | The skill states that an unfiltered `ctx_search` is not a valid index check — a miss can come from a session in another project directory, a hit from session memory (`batch:` source) — and prescribes a falsifiable alternative: a `context-mode search` with the source label whose results carry the expected `Source:` path, repeated for at least two sibling repositories in a workspace; plus an exclusion check on a term present in an excluded and in legitimate files, run with `--limit` high enough that every legitimate file (counted with `rg -l`) appears and the result count stays below the limit. | `tests/workspace-context/validate.sh` (content markers); runtime behaviour not live-tested |

### US-WC-3 — Keep public documentation truthful

As a maintainer, I want the plugin documentation and repository docs to
describe the shipped public artifact so that future changes do not reintroduce
private context.

| ID | Acceptance criterion | Test |
|---|---|---|
| AC-WC-3-1 | The plugin README explains installation, dependency scope, invocation, generated files, and safety boundaries for the public Claude Code marketplace. | Review; `tests/workspace-context/validate.sh` |
| AC-WC-3-2 | A living repository document and journal entry point to the plugin and record the source sanitization decision. | Review |

## Readiness

Readiness confidence: 95%. The source plugin files and the target marketplace
layout are known. The only implementation decision is the public, generic name
`workspace-context`; no unresolved product or interface decision blocks the
first implementation phase.
