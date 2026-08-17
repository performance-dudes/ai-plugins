---
name: iterm-dynamic-profile
description: >-
  Give every project its own terminal identity in iTerm2 — wallpaper, accent color,
  and a translucent badge in the top-right corner that shows the live Claude Code
  session name, switching automatically when you cd into the project. Covers the
  Dynamic Profiles JSON format, the Bound Hosts auto-switch, the badge/tab alpha
  pairing, background blend values that keep text readable, and how to ship a
  profile template to a team whose asset repo not everyone can clone. Use when
  someone wants per-project terminal theming, asks why their iTerm profile does not
  switch automatically, wants the session name rendered on the terminal background,
  or is packaging a terminal look for other people. Trigger phrases — "iterm
  profile", "dynamic profile", "terminal wallpaper", "per-project terminal theme",
  "session badge", "badge text", "bound hosts", "terminal background image",
  "tab color per project", "make my terminal show the session name".
---

# iTerm2 Dynamic Profiles — a terminal identity per project

A **Dynamic Profile** is a JSON file dropped into a watched folder. iTerm2 picks it
up live — no restart, no preferences dialog, and it can live in version control.

```
~/Library/Application Support/iTerm2/DynamicProfiles/<anything>.json
```

The payoff is not decoration. When you run several projects in parallel, the
terminal itself tells you which one you are looking at — before you read a single
line of text.

## The anatomy

```
┌─ what makes it "dynamic" ────────────────────────────────────┐
│                                                               │
│  Bound Hosts: ["/abs/path/to/project"]                        │
│      iTerm2 switches to this profile automatically when the   │
│      shell's working directory is inside that path.           │
│      Without it you have a theme you must choose by hand.     │
│                                                               │
├─ what you see in the top-right corner ───────────────────────┤
│                                                               │
│  Badge Text:  "<emoji> \\(session.name)"                       │
│  Badge Color: <accent>, Alpha 0.5     ← translucent           │
│  Tab Color:   <accent>, Alpha 1.0     ← same hue, solid       │
│  Use Tab Color: true                                          │
│                                                               │
├─ the backdrop ───────────────────────────────────────────────┤
│                                                               │
│  Background Image Location: /abs/path/to/image.jpg            │
│  Background Image Mode: 2 (aspect fill) | 3 (scale to fill)   │
│  Blend: ~0.10                          ← image vs. background │
│                                                               │
├─ identity ───────────────────────────────────────────────────┤
│                                                               │
│  Name, Guid ("<Name>-Dyn"), Rewritable: true                  │
│  Custom Icon Path + Icon: 2            ← tab icon             │
│  Working Directory + Custom Directory: "Yes"                  │
└───────────────────────────────────────────────────────────────┘
```

Only six values actually vary between projects: **name · emoji · accent color ·
background image · icon · project path**. Everything else is the recipe.

## The three details that carry the whole effect

### 1. `Bound Hosts` is what makes it automatic

Despite the name, this field accepts **paths**, not just hostnames. iTerm2 matches
the current working directory against them and switches profiles on its own. This
is the single field that separates "a profile I have to pick" from "the terminal
knows where I am".

It needs shell integration to report the directory. Without it the profile still
works — you just select it manually.

### 2. Badge and tab share a hue, not an alpha

```
Tab Color    #EA580C  alpha 1.00   solid, small, needs to be legible
Badge Color  #EA580C  alpha 0.50   large, behind text, must recede
```

The badge is drawn **over your terminal output**, in a large font. At full opacity
it competes with the text; at ~0.5 it reads as part of the background while staying
identifiable at a glance. Using two different colors instead breaks the association
between tab and screen — same hue, different alpha is the point.

### 3. `\(session.name)` is a live variable, not a string

The badge text is an iTerm2 interpolated string. `\(session.name)` re-renders
whenever the session name changes — which is exactly what **Claude Code's `/rename`
does**. Rename a session and the badge follows immediately.

> **Escaping:** inside JSON the backslash must be escaped, so the file contains
> `"\\(session.name)"` to produce `\(session.name)`. A single backslash silently
> yields a literal, unresolved badge.

Other useful variables: `\(session.path)`, `\(session.hostname)`,
`\(user.<name>)` for your own via the iTerm2 API.

## Choosing a background that does not hurt

A terminal wallpaper competes with the only thing that matters — the text. Three
rules from practice:

| Rule | Why |
|---|---|
| **`Blend` around 0.08–0.10** | Above ~0.25 body text starts to fight the image. Higher values only work with very flat, low-contrast art. |
| **Visual interest at the edges, calm center** | The center is where output scrolls. This is the same constraint as a video-call background, which is why call backgrounds make excellent terminal wallpapers. |
| **Set light and dark variants** | With `Use Separate Colors for Light and Dark Mode: true`, one profile survives an OS appearance switch. Otherwise your carefully chosen foreground turns unreadable at sunset. |

`Background Image Mode`: `2` = aspect fill (crops, no distortion — right for photos),
`3` = scale to fill (stretches — fine for abstract gradients).

## Shipping a profile to other people

Two things break when a profile leaves the machine it was made on:

**Absolute paths.** `Background Image Location` and `Custom Icon Path` must be
absolute. A profile with someone else's home directory in it renders **silently
without the image** — iTerm2 does not warn. Resolve paths at install time and fail
loudly when an asset is missing.

**Private asset repos.** If the wallpaper lives in a repo not everyone can clone,
the profile must degrade instead of breaking: install color, badge and icon anyway,
and say plainly that the wallpaper was skipped and where it would come from. A
teammate with a working profile minus the wallpaper is a success; a teammate staring
at an unexplained plain terminal is a support ticket.

The bundled `scripts/install-iterm-profile.sh` does both. It resolves every path,
warns per missing asset, and never clobbers an existing profile: rerunning with
unchanged input is a quiet no-op, and a profile that differs from what would be
written is left alone until you pass `--force`. That matters because iTerm2 marks
these profiles `Rewritable` — editing them by hand is expected, so a silent overwrite
would destroy exactly that work.

```bash
# from a bundled template
scripts/install-iterm-profile.sh --template performance-dudes

# or fully by hand
scripts/install-iterm-profile.sh \
  --name "My Project" --emoji "🚀" --color "#3B7DED" \
  --dir ~/Developer/my-project \
  --background ~/Developer/my-project/assets/bg.jpg
```

Templates live in `templates/*.json` and carry `{{PLACEHOLDER}}` tokens for the
machine-specific paths. `templates/performance-dudes.json` is a complete worked
example, including the case where the asset repo is private.

## Verifying

iTerm2 reloads the folder within a second — no restart. If nothing happens:

| Symptom | Cause |
|---|---|
| Profile does not appear at all | Malformed JSON. Check with `python3 -m json.tool <file>`; iTerm2 skips invalid files quietly. |
| Appears, but never activates on its own | `Bound Hosts` missing, path not absolute, or shell integration not installed. |
| Badge shows `\(session.name)` literally | Backslash not doubled in the JSON source. |
| Background stays empty | Path wrong or file unreadable. iTerm2 does not report this. |
| Two profiles fight over the same directory | Two files share a `Guid`, or nested `Bound Hosts` overlap. The deepest match wins; make the paths disjoint. |

`Rewritable: true` lets you edit the profile in the iTerm2 UI to experiment. Note
that the file is authoritative — it is rewritten on the next reload, so port any
change you want to keep back into the JSON.
