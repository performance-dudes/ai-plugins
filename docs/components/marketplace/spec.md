# Spec: Marketplace component

**Theme:** The repo exposes a valid marketplace that lists the example plugin so it
can be installed.

Hierarchy: **theme → user story (US) → acceptance criteria (AC) + test reference.**

## US-MARKETPLACE-1 — A valid marketplace that lists the plugin

> As a **user**, I want a marketplace file that lists the example plugin, so that I
> can install it with `claude plugin install example@ai-plugins`.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-MARKETPLACE-1-1 | The marketplace file exists at `.claude-plugin/marketplace.json`. | `test.sh` (file presence) |
| AC-MARKETPLACE-1-2 | It is valid JSON. | `test.sh` (`python3 -m json.tool`) |
| AC-MARKETPLACE-1-3 | It declares `name`, `owner` and `plugins`. | `test.sh` (grep fields) |
| AC-MARKETPLACE-1-4 | It lists the `example` plugin. | `test.sh` (grep `"example"`) |
