# Component: LSP server

> Code intelligence for a programming language.

## What it is

**LSP** (Language Server Protocol) brings **code intelligence** for a language:
"go to definition", error highlighting, and so on. A plugin can wire such a
language server.

## File & format

- **File:** `example/.lsp.json` (here `.lsp.json.example`).
- **Format:** `.json` — config: which command, which file extensions → which
  language.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | At **session start** — the language server starts. |
| Who triggers it? | **Automatic**, as soon as the plugin loads. |
| Where does it run? | As a separate **server process**. |

The actual server program (e.g. `gopls` for Go) must be installed **separately**,
so the example ships it defused as `.example`.

## In the example plugin (PR #1)

`.lsp.json.example` wires `gopls` (Go) as an example and maps `.go` files to the
language "go".
