# Spec: LSP-server component

**Theme:** The plugin ships a defused LSP template that shows how to wire a language
server.

## US-LSP-1 — A defused LSP template

> As a **plugin author**, I want a defused LSP template, so that I can see how a
> language server is configured.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-LSP-1-1 | The template exists at `example/.lsp.json.example`. | `test.sh` (file presence) |
| AC-LSP-1-2 | It is valid JSON. | `test.sh` (`python3 -m json.tool`) |
