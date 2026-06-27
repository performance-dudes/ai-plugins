# Spec: Theme component  *(experimental)*

**Theme:** The plugin ships an opt-in color theme.

## US-THEME-1 — An opt-in color theme

> As a **user**, I want to opt into a custom color theme, so that the interface
> matches a brand.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-THEME-1-1 | The theme file exists at `example/themes/performance-dudes.json`. | `test.sh` (file presence) |
| AC-THEME-1-2 | It is valid JSON. | `test.sh` (`python3 -m json.tool`) |
