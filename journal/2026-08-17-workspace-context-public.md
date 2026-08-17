# Public `workspace-context` plugin — 2026-08-17

**What** — Added the workspace indexing companion to the public marketplace as
`workspace-context`. It ships the explicit setup skill and the four source
templates for project-local `AGENTS.md` and `.github/hooks/` indexing without
bundling the external Context Mode runtime.

**How / decisions** — The source used a Copilot-specific layout and client
identity, so the public version uses Claude Code packaging, Performance Dudes
metadata, and the public `context-mode@context-mode` dependency. The public
plugin name is generic and the marketplace version is locked to its plugin
manifest.

**Learnings** — A focused hygiene test is useful for migrations: it checks the
real plugin files for source-marketplace and client-identity leakage while the
repository-wide scan also caught an older journal reference that needed
redaction.

**Review round** — a tandem review raised three conditions, all now met.

The hygiene check itself carried the forbidden terms. It listed them as
string-concatenated literals so the check would not match its own definition — which
also hid them from `grep`, from the check, and from one of the two reviewing agents,
which reported them as absent. It did not hide them from anyone opening the file. The
terms now live in `tests/workspace-context/hygiene-check.py` as SHA-256 prefixes; the
scan hashes every substring of the known lengths, so it still finds a term inside a
path or a compound word, and the repository no longer contains the words in any form.
Verified both ways: all five terms are found when actually present, and a clean file
does not trip it.

The lesson is worth keeping: obfuscating a secret to work around your own tooling
weakens every automated check that comes after it, while protecting nothing from a
human reader. If a value cannot be in a public file, a hash belongs there — not a
cleverer spelling of the value.

**Evals added.** A triggering suite would have been meaningless here: the skill sets
`disable-model-invocation: true` and never fires on its own, so "does it trigger"
measures a config flag that `tests/` already asserts. What varies is the judgment the
skill demands once invoked, so that is what `evals/setup-judgment/` measures — single
repository vs. multi-repository parent (with monorepo, meta-repo and worktree layouts
as the realistic traps), and whether a faulty `AGENTS.md` is recognised against the
skill's own content contract. Deterministic, ten locked tasks, one clean case.

**Claude CLI validation** — no longer outstanding: `claude plugin validate` passes for
both the plugin and the marketplace.
