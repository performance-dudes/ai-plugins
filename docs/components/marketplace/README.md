# Component: Marketplace (`marketplace.json`)

> The repo's "app store" listing: which plugins it offers and where each lives.

## What it is

A marketplace is the catalog Claude Code reads when you add this repository, so it
knows **which plugins it offers** and **where to find them**. One repo can be one
marketplace that offers many plugins.

## File & format

- **File:** `.claude-plugin/marketplace.json` — at the **repo root** (not inside
  `example/`).
- **Format:** `.json` — strict data, read by a program.

## Architecture: when read, who triggers, where it runs

| Question | Answer |
|----------|--------|
| When is it read? | When you run `claude plugin marketplace add <repo>`. |
| Who triggers it? | You — by adding the marketplace. |
| Where does it run? | Nowhere — it is **data only**, just read. |

## Fields

- **Required:** `name`, `owner` (`{ name }`), `plugins` (a list).
- **Each plugin entry:** `name` + `source` (where the plugin lives, e.g.
  `"./example"`), plus optional `description`, `version`.

## In the example plugin (PR #1)

`.claude-plugin/marketplace.json` offers one plugin: `example`, with
`source: "./example"`. That `source` means: "this plugin lives in the `example/`
subfolder of the repo."
