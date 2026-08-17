#!/usr/bin/env bash
# Install an iTerm2 Dynamic Profile — from a bundled template or from flags.
#
# Resolves every machine-specific path at install time, warns per missing asset
# instead of writing a broken path (iTerm2 renders those silently, with no image
# and no error), and is idempotent: rerunning overwrites the profile in place.
#
# Requires: bash, python3 (stdlib only — no pip, no venv).

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE_DIR="${ITERM_PROFILE_DIR:-$HOME/Library/Application Support/iTerm2/DynamicProfiles}"

TEMPLATE="" NAME="" EMOJI="" COLOR="" DIR="" BACKGROUND="" ICON="" BLEND="" DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage:
  install-iterm-profile.sh --template <name> [--dir <path>] [--dry-run]
  install-iterm-profile.sh --name <name> --emoji <e> --color <#RRGGBB> --dir <path>
                           [--background <file>] [--icon <file>] [--blend <0..1>]

Options:
  --template <name>   Use templates/<name>.json as the base (see --list).
  --name <name>       Profile name, also the tab/profile label.
  --emoji <emoji>     Prefix for the badge, e.g. 🏁 — identifies the project at a glance.
  --color <#RRGGBB>   Accent color. Tab gets alpha 1.0, badge alpha 0.5.
  --dir <path>        Project directory. Becomes Bound Hosts (auto-switch) + Working Directory.
  --background <file> Wallpaper. Omit for a profile without one.
  --icon <file>       Tab icon (PNG).
  --blend <0..1>      Image/background blend, default 0.098. Above ~0.25 text suffers.
  --list              List bundled templates and exit.
  --dry-run           Print the resulting JSON, write nothing.
  -h, --help          This text.

Templates may declare candidate paths for their assets. Missing assets are reported
and the corresponding field is left out, so the profile still installs — you get
color, badge and icon without the wallpaper, rather than a silently blank one.
USAGE
}

list_templates() {
  echo "Bundled templates:"
  for f in "$PLUGIN_ROOT"/templates/*.json; do
    [ -e "$f" ] || { echo "  (none)"; return; }
    printf '  %-24s %s\n' "$(basename "$f" .json)" \
      "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("_meta",{}).get("description",""))' "$f")"
  done
}

while [ $# -gt 0 ]; do
  case "$1" in
    --template)   TEMPLATE="$2"; shift 2 ;;
    --name)       NAME="$2"; shift 2 ;;
    --emoji)      EMOJI="$2"; shift 2 ;;
    --color)      COLOR="$2"; shift 2 ;;
    --dir)        DIR="$2"; shift 2 ;;
    --background) BACKGROUND="$2"; shift 2 ;;
    --icon)       ICON="$2"; shift 2 ;;
    --blend)      BLEND="$2"; shift 2 ;;
    --list)       list_templates; exit 0 ;;
    --dry-run)    DRY_RUN=1; shift ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$TEMPLATE" ] && [ -z "$NAME" ]; then
  echo "error: need either --template or --name" >&2
  usage >&2
  exit 2
fi

TEMPLATE_FILE=""
if [ -n "$TEMPLATE" ]; then
  TEMPLATE_FILE="$PLUGIN_ROOT/templates/$TEMPLATE.json"
  if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "error: no such template: $TEMPLATE" >&2
    list_templates >&2
    exit 2
  fi
fi

# Expand ~ and make paths absolute — iTerm2 requires absolute, and resolves nothing.
abspath() {
  [ -z "$1" ] && return 0
  local p="${1/#\~/$HOME}"
  case "$p" in /*) printf '%s' "$p" ;; *) printf '%s' "$(cd "$(dirname "$p")" 2>/dev/null && pwd)/$(basename "$p")" ;; esac
}
DIR="$(abspath "$DIR")"
BACKGROUND="$(abspath "$BACKGROUND")"
ICON="$(abspath "$ICON")"

# Only create the target directory for a real install — a --dry-run must leave the
# filesystem untouched.
[ "$DRY_RUN" = 0 ] && mkdir -p "$PROFILE_DIR"

export PD_TEMPLATE_FILE="$TEMPLATE_FILE" PD_NAME="$NAME" PD_EMOJI="$EMOJI" PD_COLOR="$COLOR" \
       PD_DIR="$DIR" PD_BACKGROUND="$BACKGROUND" PD_ICON="$ICON" PD_BLEND="$BLEND" \
       PD_PROFILE_DIR="$PROFILE_DIR" PD_DRY_RUN="$DRY_RUN" PD_HOME="$HOME"

python3 <<'PYEOF'
import json, os, sys

E = os.environ.get
HOME = E("PD_HOME")

# Progress goes to stderr, never stdout: with --dry-run stdout carries the JSON and
# must stay pipeable (`… --dry-run | python3 -m json.tool`).
def warn(msg):  print(f"  \033[33m!\033[0m {msg}", file=sys.stderr)
def ok(msg):    print(f"  \033[32m✓\033[0m {msg}", file=sys.stderr)

def srgb(hexstr, alpha=1.0):
    """#RRGGBB -> iTerm2's sRGB component dict."""
    h = hexstr.strip().lstrip("#")
    if len(h) != 6:
        sys.exit(f"error: color must be #RRGGBB, got {hexstr!r}")
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return {"Color Space": "sRGB", "Red Component": r, "Green Component": g,
            "Blue Component": b, "Alpha Component": alpha}

def first_existing(candidates):
    """Return the first candidate that exists on this machine, else None."""
    for c in candidates:
        p = os.path.expanduser(c.replace("{{HOME}}", HOME))
        if os.path.exists(p):
            return p
    return None

tpl_file = E("PD_TEMPLATE_FILE") or ""
meta = {}

if tpl_file:
    with open(tpl_file) as fh:
        doc = json.load(fh)
    meta = doc.pop("_meta", {})
    profile = doc["Profiles"][0]

    # {{HOME}} is resolved everywhere — a template must not carry the author's
    # home directory, but it may well know the conventional layout below it.
    def subst(v):
        if isinstance(v, str):  return v.replace("{{HOME}}", HOME)
        if isinstance(v, list): return [subst(x) for x in v]
        if isinstance(v, dict): return {k: subst(x) for k, x in v.items()}
        return v
    profile = subst(profile)

    # Resolve {{PLACEHOLDER}} tokens from _meta.assets — each is a list of candidate
    # paths. Missing asset -> drop the field rather than write a path that renders
    # as a blank background with no error.
    assets = meta.get("assets", {})
    for token, spec in assets.items():
        field = spec["field"]
        found = first_existing(spec.get("candidates", []))
        if found:
            profile[field] = found
            ok(f"{field}: {found}")
        else:
            profile.pop(field, None)
            # Companion keys that are meaningless without the asset — e.g. Icon: 2
            # selects "custom icon" and would leave iTerm2 pointing at nothing.
            for extra in spec.get("also_remove", []):
                profile.pop(extra, None)
            note = spec.get("missing_hint", "")
            warn(f"{field}: not found on this machine — field omitted." + (f" {note}" if note else ""))

    # The project directory may be overridden; otherwise take the template's own.
    if E("PD_DIR"):
        profile["Bound Hosts"] = [E("PD_DIR")]
        profile["Working Directory"] = E("PD_DIR")
    for key in ("Bound Hosts", "Working Directory"):
        val = profile.get(key)
        vals = val if isinstance(val, list) else [val]
        if any(isinstance(v, str) and "{{" in v for v in vals):
            sys.exit(f"error: template leaves {key} unresolved — pass --dir")
else:
    name  = E("PD_NAME")
    color = E("PD_COLOR") or "#888888"
    proj  = E("PD_DIR")
    if not proj:
        sys.exit("error: --dir is required")
    badge = f'{E("PD_EMOJI")} \\(session.name)'.strip()
    profile = {
        "Name": name,
        "Guid": name.replace(" ", "") + "-Dyn",
        "Rewritable": True,
        # Bound Hosts takes PATHS despite the name — this is the auto-switch.
        "Bound Hosts": [proj],
        "Working Directory": proj,
        "Custom Directory": "Yes",
        # Badge is an interpolated string; \(session.name) tracks Claude Code's /rename.
        "Badge Text": badge,
        "Badge Color": srgb(color, 0.5),   # translucent: sits behind the text
        "Tab Color": srgb(color, 1.0),     # solid: small, must stay legible
        "Use Tab Color": True,
        "Cursor Color": srgb(color, 1.0),
        "Blend": float(E("PD_BLEND") or 0.098),
        "Background Image Mode": 2,
    }
    if E("PD_BACKGROUND"):
        if os.path.exists(E("PD_BACKGROUND")):
            profile["Background Image Location"] = E("PD_BACKGROUND")
            ok(f"Background Image Location: {E('PD_BACKGROUND')}")
        else:
            warn(f"background not found: {E('PD_BACKGROUND')} — field omitted")
    if E("PD_ICON"):
        if os.path.exists(E("PD_ICON")):
            profile["Custom Icon Path"] = E("PD_ICON")
            profile["Icon"] = 2
            ok(f"Custom Icon Path: {E('PD_ICON')}")
        else:
            warn(f"icon not found: {E('PD_ICON')} — field omitted")

out = {"Profiles": [profile]}
text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"

if E("PD_DRY_RUN") == "1":
    print(text)
    sys.exit(0)

target = os.path.join(E("PD_PROFILE_DIR"), profile["Name"] + ".json")
existed = os.path.exists(target)
with open(target, "w") as fh:
    fh.write(text)

print(f"\n{'Updated' if existed else 'Installed'}: {target}")
print("iTerm2 reloads within a second — no restart needed.")
if hint := meta.get("after_install"):
    print(hint)
PYEOF
