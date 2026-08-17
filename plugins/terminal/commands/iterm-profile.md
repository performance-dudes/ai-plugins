---
description: Install or update an iTerm2 Dynamic Profile that gives a project its own wallpaper, accent color and session badge
---

Set up a per-project terminal identity in iTerm2 for the user.

Read the `iterm-dynamic-profile` skill first — it carries the recipe, the escaping
rules and the failure modes.

Then:

1. **Establish the target.** Which project directory? If the user did not say, use
   the current working directory. Confirm it is the directory they want the profile
   bound to — `Bound Hosts` is what makes the switch automatic, and a wrong path
   means the profile never activates.

2. **Check for a bundled template.**
   `${CLAUDE_PLUGIN_ROOT}/scripts/install-iterm-profile.sh --list`
   If one matches the project, use it — templates already carry the correct colors
   and asset candidates.

3. **Otherwise gather the six values** that vary per project: name, emoji, accent
   color, project path, background image, icon. Ask only for what you cannot infer;
   look in the repo for an existing favicon, `og-image`, or brand assets before
   asking the user to supply one.

4. **Preview, then install.** Run with `--dry-run` first and show the resulting
   JSON. On approval, rerun without it.

5. **Report honestly.** The installer warns per missing asset. Pass those warnings
   on rather than reporting plain success — a profile without its wallpaper is a
   partial result, and iTerm2 will not say so on its own.

An existing profile of the same name is overwritten in place. If the user already
has a hand-made profile for this project, say so and confirm before replacing it.
