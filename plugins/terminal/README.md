# terminal

A terminal identity per project. When several projects run in parallel, the terminal
tells you which one you are looking at — before you read a single line of output.

```
┌──────────────────────────────────────────────────────┐
│                                          🏁 auth-fix │  ← badge: emoji + live
│  $ git status                                        │    session name, accent
│  On branch main                                      │    color at alpha 0.5
│                                                      │
│  [wallpaper at Blend 0.098 — present, not loud]      │
└──────────────────────────────────────────────────────┘
   ▲ tab in the same accent color, at full opacity
```

The profile activates **on its own** when you enter the project directory, and the
badge tracks Claude Code's `/rename` live.

## Contents

| Path | What |
|---|---|
| `skills/iterm-dynamic-profile/` | The recipe: JSON format, the auto-switch, badge escaping, blend values, failure modes |
| `scripts/install-iterm-profile.sh` | Idempotent installer — resolves paths, warns per missing asset |
| `templates/performance-dudes.json` | A complete worked template, including the private-asset-repo case |
| `commands/iterm-profile.md` | `/iterm-profile` |

## Quick start

```bash
# from a bundled template
scripts/install-iterm-profile.sh --template performance-dudes

# or by hand — six values is all it takes
scripts/install-iterm-profile.sh \
  --name "My Project" --emoji "🚀" --color "#3B7DED" \
  --dir ~/Developer/my-project \
  --background ~/Developer/my-project/assets/bg.jpg \
  --icon ~/Developer/my-project/public/icon-192.png
```

`--dry-run` prints the JSON without writing. `--list` shows bundled templates.
iTerm2 picks the file up within a second; no restart.

## Why an installer instead of a JSON file to copy

iTerm2 needs **absolute** paths for the wallpaper and icon, and resolves nothing
itself. A profile authored on one machine therefore carries someone else's home
directory — and when that path does not exist, iTerm2 renders the profile **without
the image and without any error**. You get a plain terminal and no idea why.

So the installer resolves every path at install time, checks each asset, and reports
what it could not find and where that asset normally comes from. A missing wallpaper
costs you the wallpaper, not the profile.

That matters most when assets live in a repo not everyone can clone. The bundled
Performance Dudes template names its private source explicitly and falls back to
public assets, so the profile installs either way.

## Requirements

macOS, iTerm2, `python3` (stdlib only — no pip, no venv). The automatic switch also
needs iTerm2 shell integration; without it the profile works but must be selected
by hand.
